import requests
import json
import os
from datetime import datetime
from decimal import Decimal

class HomeAssistantIntegration:
    """Classe para integração com Home Assistant"""
    
    def __init__(self, ha_url=None, ha_token=None):
        self.ha_url = ha_url or os.environ.get('SUPERVISOR_URL', 'http://supervisor/core')
        self.ha_token = ha_token or os.environ.get('SUPERVISOR_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.ha_token}',
            'Content-Type': 'application/json'
        }
    
    def create_sensor(self, entity_id, name, state, attributes=None, unit_of_measurement=None):
        """Criar ou atualizar um sensor no Home Assistant"""
        try:
            data = {
                'state': str(state),
                'attributes': attributes or {}
            }
            
            if unit_of_measurement:
                data['attributes']['unit_of_measurement'] = unit_of_measurement
            
            data['attributes']['friendly_name'] = name
            data['attributes']['icon'] = attributes.get('icon', 'mdi:currency-usd')
            
            url = f"{self.ha_url}/api/states/sensor.{entity_id}"
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"Erro ao criar sensor {entity_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Erro na integração com Home Assistant: {e}")
            return False
    
    def register_service(self, domain, service, service_data):
        """Registrar um serviço no Home Assistant"""
        try:
            url = f"{self.ha_url}/api/services/{domain}/{service}"
            response = requests.post(url, headers=self.headers, json=service_data)
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"Erro ao registrar serviço {domain}.{service}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Erro ao registrar serviço: {e}")
            return False
    
    def send_notification(self, title, message, notification_id=None):
        """Enviar notificação para o Home Assistant"""
        try:
            data = {
                'title': title,
                'message': message
            }
            
            if notification_id:
                data['notification_id'] = notification_id
            
            url = f"{self.ha_url}/api/services/persistent_notification/create"
            response = requests.post(url, headers=self.headers, json=data)
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
            return False

def update_home_assistant_sensors(db_session):
    """Atualizar todos os sensores do Home Assistant com dados financeiros"""
    
    ha = HomeAssistantIntegration()
    
    try:
        from models import Account, Transaction, Category
        from sqlalchemy import func, extract
        
        # Saldo total de todas as contas
        total_balance = db_session.query(func.sum(Account.current_balance)).filter_by(is_active=True).scalar() or 0
        
        # Receitas e despesas do mês atual
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_income = db_session.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'income',
            extract('month', Transaction.transaction_date) == current_month,
            extract('year', Transaction.transaction_date) == current_year
        ).scalar() or 0
        
        monthly_expenses = db_session.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'expense',
            extract('month', Transaction.transaction_date) == current_month,
            extract('year', Transaction.transaction_date) == current_year
        ).scalar() or 0
        
        # Número de transações do mês
        monthly_transactions = db_session.query(func.count(Transaction.id)).filter(
            extract('month', Transaction.transaction_date) == current_month,
            extract('year', Transaction.transaction_date) == current_year
        ).scalar() or 0
        
        # Última transação
        last_transaction = db_session.query(Transaction).order_by(Transaction.created_at.desc()).first()
        
        # Criar/atualizar sensores
        sensors = [
            {
                'entity_id': 'finance_total_balance',
                'name': 'Saldo Total',
                'state': float(total_balance),
                'attributes': {
                    'icon': 'mdi:wallet',
                    'device_class': 'monetary',
                    'last_updated': datetime.now().isoformat()
                },
                'unit_of_measurement': 'BRL'
            },
            {
                'entity_id': 'finance_monthly_income',
                'name': 'Receitas do Mês',
                'state': float(monthly_income),
                'attributes': {
                    'icon': 'mdi:trending-up',
                    'device_class': 'monetary',
                    'month': current_month,
                    'year': current_year
                },
                'unit_of_measurement': 'BRL'
            },
            {
                'entity_id': 'finance_monthly_expenses',
                'name': 'Despesas do Mês',
                'state': float(monthly_expenses),
                'attributes': {
                    'icon': 'mdi:trending-down',
                    'device_class': 'monetary',
                    'month': current_month,
                    'year': current_year
                },
                'unit_of_measurement': 'BRL'
            },
            {
                'entity_id': 'finance_monthly_net',
                'name': 'Saldo do Mês',
                'state': float(monthly_income - monthly_expenses),
                'attributes': {
                    'icon': 'mdi:chart-line',
                    'device_class': 'monetary',
                    'income': float(monthly_income),
                    'expenses': float(monthly_expenses)
                },
                'unit_of_measurement': 'BRL'
            },
            {
                'entity_id': 'finance_monthly_transactions',
                'name': 'Transações do Mês',
                'state': monthly_transactions,
                'attributes': {
                    'icon': 'mdi:swap-horizontal',
                    'month': current_month,
                    'year': current_year
                }
            }
        ]
        
        # Adicionar sensor da última transação se existir
        if last_transaction:
            sensors.append({
                'entity_id': 'finance_last_transaction',
                'name': 'Última Transação',
                'state': last_transaction.description,
                'attributes': {
                    'icon': 'mdi:receipt',
                    'amount': float(last_transaction.amount),
                    'type': last_transaction.transaction_type,
                    'date': last_transaction.transaction_date.isoformat(),
                    'account': last_transaction.account.name if last_transaction.account else None,
                    'category': last_transaction.category.name if last_transaction.category else None
                }
            })
        
        # Criar todos os sensores
        success_count = 0
        for sensor in sensors:
            if ha.create_sensor(**sensor):
                success_count += 1
        
        print(f"Sensores atualizados: {success_count}/{len(sensors)}")
        return success_count == len(sensors)
        
    except Exception as e:
        print(f"Erro ao atualizar sensores: {e}")
        return False

def register_home_assistant_services():
    """Registrar serviços do Home Assistant para interagir com o sistema financeiro"""
    
    ha = HomeAssistantIntegration()
    
    services = [
        {
            'domain': 'finance_manager',
            'service': 'add_expense',
            'service_data': {
                'description': 'Adicionar nova despesa',
                'fields': {
                    'description': {
                        'description': 'Descrição da despesa',
                        'example': 'Compra no supermercado'
                    },
                    'amount': {
                        'description': 'Valor da despesa',
                        'example': 150.50
                    },
                    'category': {
                        'description': 'Categoria da despesa',
                        'example': 'Alimentação'
                    },
                    'account': {
                        'description': 'Conta da despesa',
                        'example': 'Conta Corrente'
                    }
                }
            }
        },
        {
            'domain': 'finance_manager',
            'service': 'add_income',
            'service_data': {
                'description': 'Adicionar nova receita',
                'fields': {
                    'description': {
                        'description': 'Descrição da receita',
                        'example': 'Salário'
                    },
                    'amount': {
                        'description': 'Valor da receita',
                        'example': 3000.00
                    },
                    'category': {
                        'description': 'Categoria da receita',
                        'example': 'Salário'
                    },
                    'account': {
                        'description': 'Conta da receita',
                        'example': 'Conta Corrente'
                    }
                }
            }
        }
    ]
    
    success_count = 0
    for service in services:
        if ha.register_service(service['domain'], service['service'], service['service_data']):
            success_count += 1
    
    print(f"Serviços registrados: {success_count}/{len(services)}")
    return success_count == len(services)

def handle_home_assistant_service_call(service_name, service_data, db_session):
    """Processar chamadas de serviço do Home Assistant"""
    
    try:
        from models import Account, Category, Transaction
        
        if service_name == 'add_expense':
            return add_transaction_from_service('expense', service_data, db_session)
        elif service_name == 'add_income':
            return add_transaction_from_service('income', service_data, db_session)
        else:
            return False, f"Serviço desconhecido: {service_name}"
            
    except Exception as e:
        return False, f"Erro ao processar serviço: {e}"

def add_transaction_from_service(transaction_type, service_data, db_session):
    """Adicionar transação através de serviço do Home Assistant"""
    
    try:
        from models import Account, Category, Transaction
        
        # Buscar conta
        account_name = service_data.get('account', 'Conta Corrente')
        account = db_session.query(Account).filter_by(name=account_name, is_active=True).first()
        
        if not account:
            return False, f"Conta '{account_name}' não encontrada"
        
        # Buscar categoria
        category_name = service_data.get('category')
        category = db_session.query(Category).filter_by(
            name=category_name, 
            category_type=transaction_type,
            is_active=True
        ).first()
        
        if not category:
            return False, f"Categoria '{category_name}' não encontrada para {transaction_type}"
        
        # Criar transação
        transaction = Transaction(
            description=service_data['description'],
            amount=Decimal(str(service_data['amount'])),
            transaction_type=transaction_type,
            transaction_date=datetime.now().date(),
            account_id=account.id,
            category_id=category.id
        )
        
        db_session.add(transaction)
        
        # Atualizar saldo da conta
        if transaction_type == 'income':
            account.current_balance += transaction.amount
        else:
            account.current_balance -= transaction.amount
        
        db_session.commit()
        
        # Atualizar sensores
        update_home_assistant_sensors(db_session)
        
        # Enviar notificação
        ha = HomeAssistantIntegration()
        ha.send_notification(
            title="Nova Transação",
            message=f"{transaction.description}: R$ {transaction.amount}",
            notification_id="finance_transaction"
        )
        
        return True, "Transação adicionada com sucesso"
        
    except Exception as e:
        db_session.rollback()
        return False, f"Erro ao adicionar transação: {e}"

