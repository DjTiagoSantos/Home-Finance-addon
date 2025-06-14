from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
from decimal import Decimal
import os
import logging
import threading
import time

# Importar modelos e integração
from models import db, Account, Category, Transaction, Budget, RecurringTransaction
from home_assistant_integration import (
    update_home_assistant_sensors, 
    register_home_assistant_services,
    handle_home_assistant_service_call
)

def create_app():
    """Factory function para criar a aplicação Flask"""
    # Definir caminhos corretos para templates e static
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Configurações
    database_path = os.environ.get('DATABASE_PATH', '/data/finance.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'home-finance-secret-key'
    
    # Configurar logging
    log_level = os.environ.get('LOG_LEVEL', 'info').upper()
    logging.basicConfig(level=getattr(logging, log_level))
    
    # Inicializar extensões
    db.init_app(app)
    CORS(app, origins="*")  # Permitir CORS para todas as origens
    
    # Registrar blueprints/rotas
    register_routes(app)
    
    # Inicializar integração com Home Assistant
    initialize_home_assistant_integration(app)
    
    return app

def initialize_home_assistant_integration(app):
    """Inicializar integração com Home Assistant"""
    def setup_integration():
        time.sleep(5)  # Aguardar aplicação inicializar
        with app.app_context():
            try:
                # Registrar serviços
                register_home_assistant_services()
                
                # Atualizar sensores iniciais
                update_home_assistant_sensors(db.session)
                
                print("Integração com Home Assistant inicializada com sucesso!")
            except Exception as e:
                print(f"Erro na integração com Home Assistant: {e}")
    
    # Executar em thread separada para não bloquear a aplicação
    thread = threading.Thread(target=setup_integration)
    thread.daemon = True
    thread.start()

def register_routes(app):
    """Registra todas as rotas da aplicação"""
    
    @app.route('/')
    def index():
        """Página principal"""
        return render_template('index.html')
    
    # === ROTAS DE CONTAS ===
    
    @app.route('/api/accounts', methods=['GET'])
    def get_accounts():
        """Listar todas as contas"""
        accounts = Account.query.filter_by(is_active=True).all()
        return jsonify([account.to_dict() for account in accounts])
    
    @app.route('/api/accounts', methods=['POST'])
    def create_account():
        """Criar nova conta"""
        data = request.get_json()
        
        account = Account(
            name=data['name'],
            account_type=data['account_type'],
            initial_balance=Decimal(str(data.get('initial_balance', 0))),
            current_balance=Decimal(str(data.get('initial_balance', 0)))
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify(account.to_dict()), 201
    
    @app.route('/api/accounts/<int:account_id>', methods=['PUT'])
    def update_account(account_id):
        """Atualizar conta"""
        account = Account.query.get_or_404(account_id)
        data = request.get_json()
        
        account.name = data.get('name', account.name)
        account.account_type = data.get('account_type', account.account_type)
        
        db.session.commit()
        return jsonify(account.to_dict())
    
    @app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
    def delete_account(account_id):
        """Desativar conta"""
        account = Account.query.get_or_404(account_id)
        account.is_active = False
        db.session.commit()
        return '', 204
    
    # === ROTAS DE CATEGORIAS ===
    
    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        """Listar todas as categorias"""
        category_type = request.args.get('type')  # income ou expense
        query = Category.query.filter_by(is_active=True)
        
        if category_type:
            query = query.filter_by(category_type=category_type)
        
        categories = query.all()
        return jsonify([category.to_dict() for category in categories])
    
    @app.route('/api/categories', methods=['POST'])
    def create_category():
        """Criar nova categoria"""
        data = request.get_json()
        
        category = Category(
            name=data['name'],
            category_type=data['category_type'],
            color=data.get('color', '#007bff'),
            icon=data.get('icon', 'fas fa-tag')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify(category.to_dict()), 201
    
    @app.route('/api/categories/<int:category_id>', methods=['PUT'])
    def update_category(category_id):
        """Atualizar categoria"""
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        category.name = data.get('name', category.name)
        category.color = data.get('color', category.color)
        category.icon = data.get('icon', category.icon)
        
        db.session.commit()
        return jsonify(category.to_dict())
    
    @app.route('/api/categories/<int:category_id>', methods=['DELETE'])
    def delete_category(category_id):
        """Desativar categoria"""
        category = Category.query.get_or_404(category_id)
        category.is_active = False
        db.session.commit()
        return '', 204
    
    # === ROTAS DE TRANSAÇÕES ===
    
    @app.route('/api/transactions', methods=['GET'])
    def get_transactions():
        """Listar transações com filtros opcionais"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        account_id = request.args.get('account_id', type=int)
        category_id = request.args.get('category_id', type=int)
        transaction_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Transaction.query
        
        if account_id:
            query = query.filter_by(account_id=account_id)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        if start_date:
            query = query.filter(Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        query = query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        
        transactions = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    @app.route('/api/transactions', methods=['POST'])
    def create_transaction():
        """Criar nova transação"""
        data = request.get_json()
        
        transaction = Transaction(
            description=data['description'],
            amount=Decimal(str(data['amount'])),
            transaction_type=data['transaction_type'],
            transaction_date=datetime.strptime(data['transaction_date'], '%Y-%m-%d').date(),
            notes=data.get('notes'),
            account_id=data['account_id'],
            category_id=data['category_id']
        )
        
        db.session.add(transaction)
        
        # Atualizar saldo da conta
        account = Account.query.get(data['account_id'])
        if data['transaction_type'] == 'income':
            account.current_balance += transaction.amount
        else:
            account.current_balance -= transaction.amount
        
        db.session.commit()
        
        # Atualizar sensores do Home Assistant
        try:
            update_home_assistant_sensors(db.session)
        except Exception as e:
            print(f"Erro ao atualizar sensores: {e}")
        
        return jsonify(transaction.to_dict()), 201
    
    @app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
    def update_transaction(transaction_id):
        """Atualizar transação"""
        transaction = Transaction.query.get_or_404(transaction_id)
        data = request.get_json()
        
        # Reverter o impacto no saldo da conta anterior
        old_account = Account.query.get(transaction.account_id)
        if transaction.transaction_type == 'income':
            old_account.current_balance -= transaction.amount
        else:
            old_account.current_balance += transaction.amount
        
        # Atualizar dados da transação
        transaction.description = data.get('description', transaction.description)
        transaction.amount = Decimal(str(data.get('amount', transaction.amount)))
        transaction.transaction_type = data.get('transaction_type', transaction.transaction_type)
        transaction.transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date() if 'transaction_date' in data else transaction.transaction_date
        transaction.notes = data.get('notes', transaction.notes)
        transaction.account_id = data.get('account_id', transaction.account_id)
        transaction.category_id = data.get('category_id', transaction.category_id)
        transaction.updated_at = datetime.utcnow()
        
        # Aplicar novo impacto no saldo
        new_account = Account.query.get(transaction.account_id)
        if transaction.transaction_type == 'income':
            new_account.current_balance += transaction.amount
        else:
            new_account.current_balance -= transaction.amount
        
        db.session.commit()
        
        # Atualizar sensores do Home Assistant
        try:
            update_home_assistant_sensors(db.session)
        except Exception as e:
            print(f"Erro ao atualizar sensores: {e}")
            
        return jsonify(transaction.to_dict())
    
    @app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
    def delete_transaction(transaction_id):
        """Excluir transação"""
        transaction = Transaction.query.get_or_404(transaction_id)
        
        # Reverter o impacto no saldo da conta
        account = Account.query.get(transaction.account_id)
        if transaction.transaction_type == 'income':
            account.current_balance -= transaction.amount
        else:
            account.current_balance += transaction.amount
        
        db.session.delete(transaction)
        db.session.commit()
        
        # Atualizar sensores do Home Assistant
        try:
            update_home_assistant_sensors(db.session)
        except Exception as e:
            print(f"Erro ao atualizar sensores: {e}")
            
        return '', 204
    
    # === ROTAS DE RELATÓRIOS ===
    
    @app.route('/api/reports/summary', methods=['GET'])
    def get_summary():
        """Resumo financeiro geral"""
        # Saldo total de todas as contas
        total_balance = db.session.query(db.func.sum(Account.current_balance)).filter_by(is_active=True).scalar() or 0
        
        # Receitas e despesas do mês atual
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_income = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'income',
            db.extract('month', Transaction.transaction_date) == current_month,
            db.extract('year', Transaction.transaction_date) == current_year
        ).scalar() or 0
        
        monthly_expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'expense',
            db.extract('month', Transaction.transaction_date) == current_month,
            db.extract('year', Transaction.transaction_date) == current_year
        ).scalar() or 0
        
        return jsonify({
            'total_balance': float(total_balance),
            'monthly_income': float(monthly_income),
            'monthly_expenses': float(monthly_expenses),
            'monthly_net': float(monthly_income - monthly_expenses)
        })
    
    @app.route('/api/reports/expenses-by-category', methods=['GET'])
    def get_expenses_by_category():
        """Despesas por categoria no período especificado"""
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = db.session.query(
            Category.name,
            Category.color,
            db.func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            Transaction.transaction_type == 'expense'
        )
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Transaction.transaction_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        results = query.group_by(Category.id).all()
        
        return jsonify([{
            'category': result.name,
            'color': result.color,
            'amount': float(result.total)
        } for result in results])

    # === ROTAS DE SERVIÇOS DO HOME ASSISTANT ===
    
    @app.route('/api/home-assistant/service/<service_name>', methods=['POST'])
    def handle_ha_service(service_name):
        """Processar chamadas de serviço do Home Assistant"""
        try:
            service_data = request.get_json()
            success, message = handle_home_assistant_service_call(service_name, service_data, db.session)
            
            if success:
                return jsonify({'success': True, 'message': message}), 200
            else:
                return jsonify({'success': False, 'error': message}), 400
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/home-assistant/sensors/update', methods=['POST'])
    def update_ha_sensors():
        """Atualizar manualmente todos os sensores do Home Assistant"""
        try:
            success = update_home_assistant_sensors(db.session)
            if success:
                return jsonify({'success': True, 'message': 'Sensores atualizados com sucesso'}), 200
            else:
                return jsonify({'success': False, 'error': 'Erro ao atualizar sensores'}), 500
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app = create_app()
    
    # Criar tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    # Executar aplicação
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

