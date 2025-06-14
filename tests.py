import unittest
import json
import tempfile
import os
from datetime import datetime, date
from decimal import Decimal

# Configurar path para importar módulos
import sys
sys.path.append('/home/ubuntu/home-finance-addon/app')

from main import create_app
from models import db, Account, Category, Transaction

class FinanceManagerTestCase(unittest.TestCase):
    """Testes para o Home Finance Manager"""
    
    def setUp(self):
        """Configurar ambiente de teste"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Configurar aplicação para teste
        os.environ['DATABASE_PATH'] = self.db_path
        os.environ['LOG_LEVEL'] = 'error'
        os.environ['PORT'] = '5002'
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()
    
    def tearDown(self):
        """Limpar ambiente de teste"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_test_data(self):
        """Criar dados de teste"""
        # Criar conta de teste
        account = Account(
            name="Conta Teste",
            account_type="checking",
            initial_balance=1000.00,
            current_balance=1000.00
        )
        db.session.add(account)
        
        # Criar categoria de teste
        category = Category(
            name="Categoria Teste",
            category_type="expense",
            color="#FF0000",
            icon="fas fa-test"
        )
        db.session.add(category)
        
        db.session.commit()
        
        self.test_account_id = account.id
        self.test_category_id = category.id
    
    def test_get_accounts(self):
        """Testar listagem de contas"""
        response = self.client.get('/api/accounts')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]['name'], 'Conta Teste')
    
    def test_create_account(self):
        """Testar criação de conta"""
        account_data = {
            'name': 'Nova Conta',
            'account_type': 'savings',
            'initial_balance': 500.00
        }
        
        response = self.client.post('/api/accounts', 
                                  data=json.dumps(account_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Nova Conta')
        self.assertEqual(data['account_type'], 'savings')
        self.assertEqual(data['current_balance'], 500.00)
    
    def test_get_categories(self):
        """Testar listagem de categorias"""
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_create_category(self):
        """Testar criação de categoria"""
        category_data = {
            'name': 'Nova Categoria',
            'category_type': 'income',
            'color': '#00FF00',
            'icon': 'fas fa-money'
        }
        
        response = self.client.post('/api/categories',
                                  data=json.dumps(category_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Nova Categoria')
        self.assertEqual(data['category_type'], 'income')
    
    def test_create_transaction(self):
        """Testar criação de transação"""
        transaction_data = {
            'description': 'Transação de Teste',
            'amount': 100.50,
            'transaction_type': 'expense',
            'transaction_date': '2025-06-13',
            'account_id': self.test_account_id,
            'category_id': self.test_category_id
        }
        
        response = self.client.post('/api/transactions',
                                  data=json.dumps(transaction_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['description'], 'Transação de Teste')
        self.assertEqual(data['amount'], 100.50)
        self.assertEqual(data['transaction_type'], 'expense')
    
    def test_get_transactions(self):
        """Testar listagem de transações"""
        # Primeiro criar uma transação
        self.test_create_transaction()
        
        response = self.client.get('/api/transactions')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('transactions', data)
        self.assertIsInstance(data['transactions'], list)
    
    def test_update_transaction(self):
        """Testar atualização de transação"""
        # Criar transação primeiro
        transaction_data = {
            'description': 'Transação Original',
            'amount': 50.00,
            'transaction_type': 'expense',
            'transaction_date': '2025-06-13',
            'account_id': self.test_account_id,
            'category_id': self.test_category_id
        }
        
        create_response = self.client.post('/api/transactions',
                                         data=json.dumps(transaction_data),
                                         content_type='application/json')
        
        transaction_id = json.loads(create_response.data)['id']
        
        # Atualizar transação
        update_data = {
            'description': 'Transação Atualizada',
            'amount': 75.00,
            'transaction_type': 'expense',
            'transaction_date': '2025-06-13',
            'account_id': self.test_account_id,
            'category_id': self.test_category_id
        }
        
        response = self.client.put(f'/api/transactions/{transaction_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['description'], 'Transação Atualizada')
        self.assertEqual(data['amount'], 75.00)
    
    def test_delete_transaction(self):
        """Testar exclusão de transação"""
        # Criar transação primeiro
        transaction_data = {
            'description': 'Transação para Deletar',
            'amount': 25.00,
            'transaction_type': 'expense',
            'transaction_date': '2025-06-13',
            'account_id': self.test_account_id,
            'category_id': self.test_category_id
        }
        
        create_response = self.client.post('/api/transactions',
                                         data=json.dumps(transaction_data),
                                         content_type='application/json')
        
        transaction_id = json.loads(create_response.data)['id']
        
        # Deletar transação
        response = self.client.delete(f'/api/transactions/{transaction_id}')
        self.assertEqual(response.status_code, 204)
    
    def test_get_summary(self):
        """Testar relatório de resumo"""
        response = self.client.get('/api/reports/summary')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('total_balance', data)
        self.assertIn('monthly_income', data)
        self.assertIn('monthly_expenses', data)
        self.assertIn('monthly_net', data)
    
    def test_get_expenses_by_category(self):
        """Testar relatório de despesas por categoria"""
        response = self.client.get('/api/reports/expenses-by-category')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_account_balance_update(self):
        """Testar atualização de saldo da conta após transação"""
        # Obter saldo inicial
        account_response = self.client.get('/api/accounts')
        initial_balance = json.loads(account_response.data)[0]['current_balance']
        
        # Criar transação de despesa
        transaction_data = {
            'description': 'Teste Saldo',
            'amount': 100.00,
            'transaction_type': 'expense',
            'transaction_date': '2025-06-13',
            'account_id': self.test_account_id,
            'category_id': self.test_category_id
        }
        
        self.client.post('/api/transactions',
                        data=json.dumps(transaction_data),
                        content_type='application/json')
        
        # Verificar saldo atualizado
        account_response = self.client.get('/api/accounts')
        new_balance = json.loads(account_response.data)[0]['current_balance']
        
        self.assertEqual(new_balance, initial_balance - 100.00)
    
    def test_transaction_filters(self):
        """Testar filtros de transações"""
        # Criar algumas transações
        transactions = [
            {
                'description': 'Receita Teste',
                'amount': 200.00,
                'transaction_type': 'income',
                'transaction_date': '2025-06-13',
                'account_id': self.test_account_id,
                'category_id': self.test_category_id
            },
            {
                'description': 'Despesa Teste',
                'amount': 50.00,
                'transaction_type': 'expense',
                'transaction_date': '2025-06-13',
                'account_id': self.test_account_id,
                'category_id': self.test_category_id
            }
        ]
        
        for transaction in transactions:
            self.client.post('/api/transactions',
                           data=json.dumps(transaction),
                           content_type='application/json')
        
        # Testar filtro por tipo
        response = self.client.get('/api/transactions?type=income')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        income_transactions = [t for t in data['transactions'] if t['transaction_type'] == 'income']
        self.assertGreater(len(income_transactions), 0)
    
    def test_pagination(self):
        """Testar paginação de transações"""
        response = self.client.get('/api/transactions?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('transactions', data)
        self.assertIn('total', data)
        self.assertIn('pages', data)
        self.assertIn('current_page', data)
        self.assertIn('per_page', data)

if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2)

