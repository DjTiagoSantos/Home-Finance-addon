import os
import sqlite3
from datetime import datetime
from models import db, Account, Category, Transaction, Budget

def init_database():
    """Inicializa o banco de dados com dados padrão"""
    
    # Criar todas as tabelas
    db.create_all()
    
    # Verificar se já existem dados
    if Account.query.first() is not None:
        print("Banco de dados já inicializado.")
        return
    
    print("Inicializando banco de dados com dados padrão...")
    
    # Criar contas padrão
    default_accounts = [
        Account(name="Conta Corrente", account_type="checking", initial_balance=0.00, current_balance=0.00),
        Account(name="Poupança", account_type="savings", initial_balance=0.00, current_balance=0.00),
        Account(name="Cartão de Crédito", account_type="credit_card", initial_balance=0.00, current_balance=0.00),
        Account(name="Dinheiro", account_type="cash", initial_balance=0.00, current_balance=0.00)
    ]
    
    for account in default_accounts:
        db.session.add(account)
    
    # Criar categorias padrão de despesas
    expense_categories = [
        Category(name="Alimentação", category_type="expense", color="#FF6B6B", icon="fas fa-utensils"),
        Category(name="Transporte", category_type="expense", color="#4ECDC4", icon="fas fa-car"),
        Category(name="Moradia", category_type="expense", color="#45B7D1", icon="fas fa-home"),
        Category(name="Saúde", category_type="expense", color="#96CEB4", icon="fas fa-heartbeat"),
        Category(name="Educação", category_type="expense", color="#FFEAA7", icon="fas fa-graduation-cap"),
        Category(name="Lazer", category_type="expense", color="#DDA0DD", icon="fas fa-gamepad"),
        Category(name="Vestuário", category_type="expense", color="#FFB6C1", icon="fas fa-tshirt"),
        Category(name="Serviços", category_type="expense", color="#F0E68C", icon="fas fa-tools"),
        Category(name="Impostos", category_type="expense", color="#CD5C5C", icon="fas fa-file-invoice-dollar"),
        Category(name="Outros", category_type="expense", color="#D3D3D3", icon="fas fa-ellipsis-h")
    ]
    
    for category in expense_categories:
        db.session.add(category)
    
    # Criar categorias padrão de receitas
    income_categories = [
        Category(name="Salário", category_type="income", color="#32CD32", icon="fas fa-money-bill-wave"),
        Category(name="Freelance", category_type="income", color="#90EE90", icon="fas fa-laptop"),
        Category(name="Investimentos", category_type="income", color="#228B22", icon="fas fa-chart-line"),
        Category(name="Vendas", category_type="income", color="#98FB98", icon="fas fa-shopping-cart"),
        Category(name="Presentes", category_type="income", color="#00FF7F", icon="fas fa-gift"),
        Category(name="Outros", category_type="income", color="#ADFF2F", icon="fas fa-plus-circle")
    ]
    
    for category in income_categories:
        db.session.add(category)
    
    # Commit das mudanças
    db.session.commit()
    print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    app = Flask(__name__)
    
    # Configuração do banco de dados
    database_path = os.environ.get('DATABASE_PATH', '/data/finance.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        init_database()

