"""
Home Finance Integration for Home Assistant.
Controle suas finanças pessoais diretamente no Home Assistant.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "home_finance"
PLATFORMS = [Platform.SENSOR]

# Configuração via YAML
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Optional("accounts", default=[]): vol.All(cv.ensure_list, [
                vol.Schema({
                    vol.Required("name"): str,
                    vol.Required("type"): vol.In(["conta_corrente", "poupanca", "investimento", "cartao"]),
                    vol.Optional("initial_balance", default=0): vol.Coerce(float),
                })
            ]),
            vol.Optional("categories", default=[]): vol.All(cv.ensure_list, [
                vol.Schema({
                    vol.Required("name"): str,
                    vol.Required("type"): vol.In(["receita", "despesa"]),
                    vol.Optional("budget_limit"): vol.Coerce(float),
                })
            ])
        })
    },
    extra=vol.ALLOW_EXTRA,
)

class HomeFinanceData:
    """Gerenciador de dados do Home Finance."""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.transactions: list = []
        self.categories: Dict[str, Dict[str, Any]] = {}
        
    def add_account(self, name: str, account_type: str, initial_balance: float = 0):
        """Adiciona uma nova conta."""
        self.accounts[name] = {
            "type": account_type,
            "balance": initial_balance,
            "initial_balance": initial_balance,
            "created_at": datetime.now()
        }
        _LOGGER.info(f"Conta adicionada: {name} ({account_type})")
        
    def add_transaction(self, account: str, amount: float, description: str, 
                       category: str = "Geral", transaction_type: str = "expense"):
        """Adiciona uma transação."""
        if account not in self.accounts:
            _LOGGER.error(f"Conta {account} não encontrada")
            return False
            
        transaction = {
            "id": len(self.transactions) + 1,
            "account": account,
            "amount": amount,
            "description": description,
            "category": category,
            "type": transaction_type,
            "date": datetime.now(),
        }
        
        self.transactions.append(transaction)
        
        # Atualiza saldo da conta
        if transaction_type == "income":
            self.accounts[account]["balance"] += amount
        else:
            self.accounts[account]["balance"] -= amount
            
        _LOGGER.info(f"Transação adicionada: {description} - R$ {amount}")
        return True
        
    def get_account_balance(self, account: str) -> float:
        """Retorna o saldo da conta."""
        return self.accounts.get(account, {}).get("balance", 0)
        
    def get_monthly_summary(self, month: int = None, year: int = None) -> Dict[str, float]:
        """Retorna resumo mensal."""
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
            
        monthly_transactions = [
            t for t in self.transactions 
            if t["date"].month == month and t["date"].year == year
        ]
        
        income = sum(t["amount"] for t in monthly_transactions if t["type"] == "income")
        expenses = sum(t["amount"] for t in monthly_transactions if t["type"] == "expense")
        
        return {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "transactions_count": len(monthly_transactions)
        }

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Configura a integração Home Finance."""
    
    # Inicializa dados
    finance_data = HomeFinanceData(hass)
    hass.data[DOMAIN] = finance_data
    
    # Configura contas do YAML
    domain_config = config.get(DOMAIN, {})
    
    for account_config in domain_config.get("accounts", []):
        finance_data.add_account(
            account_config["name"],
            account_config["type"],
            account_config.get("initial_balance", 0)
        )
    
    # Configura categorias
    for category_config in domain_config.get("categories", []):
        finance_data.categories[category_config["name"]] = {
            "type": category_config["type"],
            "budget_limit": category_config.get("budget_limit")
        }
    
    # Registra serviços
    async def add_transaction_service(call: ServiceCall):
        """Serviço para adicionar transação."""
        account = call.data.get("account")
        amount = call.data.get("amount")
        description = call.data.get("description")
        category = call.data.get("category", "Geral")
        transaction_type = call.data.get("type", "expense")
        
        success = finance_data.add_transaction(
            account, amount, description, category, transaction_type
        )
        
        if success:
            # Atualiza sensores
            hass.bus.async_fire(f"{DOMAIN}_transaction_added", {
                "account": account,
                "amount": amount,
                "description": description
            })
    
    async def add_account_service(call: ServiceCall):
        """Serviço para adicionar conta."""
        name = call.data.get("name")
        account_type = call.data.get("type")
        initial_balance = call.data.get("initial_balance", 0)
        
        finance_data.add_account(name, account_type, initial_balance)
        
        # Atualiza sensores
        hass.bus.async_fire(f"{DOMAIN}_account_added", {
            "name": name,
            "type": account_type
        })
    
    # Registra os serviços
    hass.services.async_register(
        DOMAIN, "add_transaction", add_transaction_service,
        schema=vol.Schema({
            vol.Required("account"): str,
            vol.Required("amount"): vol.Coerce(float),
            vol.Required("description"): str,
            vol.Optional("category", default="Geral"): str,
            vol.Optional("type", default="expense"): vol.In(["income", "expense"]),
        })
    )
    
    hass.services.async_register(
        DOMAIN, "add_account", add_account_service,
        schema=vol.Schema({
            vol.Required("name"): str,
            vol.Required("type"): vol.In(["conta_corrente", "poupanca", "investimento", "cartao"]),
            vol.Optional("initial_balance", default=0): vol.Coerce(float),
        })
    )
    
    # Carrega plataformas
    await hass.helpers.discovery.async_load_platform(Platform.SENSOR, DOMAIN, {}, config)
    
    return True
