from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()

class Account(db.Model):
    """Modelo para contas financeiras (Corrente, Poupança, Cartão, etc.)"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # checking, savings, credit_card, cash
    initial_balance = db.Column(db.Numeric(10, 2), default=0.00)
    current_balance = db.Column(db.Numeric(10, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    
    def __repr__(self):
        return f'<Account {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type,
            'initial_balance': float(self.initial_balance),
            'current_balance': float(self.current_balance),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    """Modelo para categorias de transações"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_type = db.Column(db.String(20), nullable=False)  # income, expense
    color = db.Column(db.String(7), default='#007bff')  # Cor em hexadecimal
    icon = db.Column(db.String(50), default='fas fa-tag')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_type': self.category_type,
            'color': self.color,
            'icon': self.icon,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Transaction(db.Model):
    """Modelo para transações financeiras"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # income, expense
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    notes = db.Column(db.Text)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20))  # monthly, weekly, yearly
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chaves estrangeiras
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    def __repr__(self):
        return f'<Transaction {self.description}: {self.amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat(),
            'notes': self.notes,
            'is_recurring': self.is_recurring,
            'recurring_frequency': self.recurring_frequency,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'account_name': self.account.name if self.account else None,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Budget(db.Model):
    """Modelo para orçamentos por categoria"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    budgeted_amount = db.Column(db.Numeric(10, 2), nullable=False)
    spent_amount = db.Column(db.Numeric(10, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Índice único para evitar orçamentos duplicados
    __table_args__ = (db.UniqueConstraint('category_id', 'month', 'year', name='unique_budget_per_month'),)
    
    def __repr__(self):
        return f'<Budget {self.category.name}: {self.budgeted_amount} ({self.month}/{self.year})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'month': self.month,
            'year': self.year,
            'budgeted_amount': float(self.budgeted_amount),
            'spent_amount': float(self.spent_amount),
            'remaining_amount': float(self.budgeted_amount - self.spent_amount),
            'percentage_used': float((self.spent_amount / self.budgeted_amount) * 100) if self.budgeted_amount > 0 else 0,
            'is_active': self.is_active,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat()
        }

class RecurringTransaction(db.Model):
    """Modelo para transações recorrentes"""
    __tablename__ = 'recurring_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # income, expense
    frequency = db.Column(db.String(20), nullable=False)  # monthly, weekly, yearly
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # Opcional
    next_execution = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    def __repr__(self):
        return f'<RecurringTransaction {self.description}: {self.amount} ({self.frequency})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_execution': self.next_execution.isoformat(),
            'is_active': self.is_active,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat()
        }

