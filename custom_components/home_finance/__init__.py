"""
Home Finance Integration for Home Assistant.
Controle suas finanças pessoais diretamente no Home Assistant.
"""
import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util
from homeassistant.helpers.dispatcher import async_dispatcher_send

_LOGGER = logging.getLogger(__name__)

DOMAIN = "home_finance"
PLATFORMS = [Platform.SENSOR]

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
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._store = Store(hass, 1, f"{DOMAIN}_data.json")
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.transactions: list = []
        self.categories: Dict[str, Dict[str, Any]] = {}

    async def async_load(self):
        data = await self._store.async_load()
        if data:
            self.accounts = data.get("accounts", {})
            self.transactions = data.get("transactions", [])
            self.categories = data.get("categories", {})

    async def async_save(self):
        await self._store.async_save({
            "accounts": self.accounts,
            "transactions": self.transactions,
            "categories": self.categories
        })

    async def add_account(self, name: str, account_type: str, initial_balance: float = 0):
        self.accounts[name] = {
            "type": account_type,
            "balance": initial_balance,
            "initial_balance": initial_balance,
            "created_at": datetime.now().isoformat()
        }
        await self.async_save()
        _LOGGER.info(f"Conta adicionada: {name} ({account_type})")

    async def add_transaction(self, account: str, amount: float, description: str,
                              category: str = "Geral", transaction_type: str = "expense",
                              due_date: Optional[date] = None):
        if account not in self.accounts:
            _LOGGER.error(f"Conta {account} não encontrada")
            return False

        if due_date and isinstance(due_date, datetime):
            due_date = due_date.date()

        transaction = {
            "id": len(self.transactions) + 1,
            "account": account,
            "amount": amount,
            "description": description,
            "category": category,
            "type": transaction_type,
            "date": datetime.now().isoformat(),
            "due_date": due_date.isoformat() if due_date else None,
            "paid": False
        }

        self.transactions.append(transaction)

        if transaction_type == "income":
            self.accounts[account]["balance"] += amount
        else:
            self.accounts[account]["balance"] -= amount

        await self.async_save()
        _LOGGER.info(f"Transação adicionada: {description} - R$ {amount}")
        return True

    async def mark_transaction_paid(self, tx_id: int):
        for tx in self.transactions:
            if tx["id"] == tx_id:
                tx["paid"] = True
                await self.async_save()
                _LOGGER.info(f"Transação {tx_id} marcada como paga")
                return True
        return False

    async def reset_transactions(self):
        self.transactions.clear()
        for account in self.accounts.values():
            account["balance"] = account["initial_balance"]
        await self.async_save()

    def get_account_balance(self, account: str) -> float:
        return self.accounts.get(account, {}).get("balance", 0)

    def get_due_transactions(self, from_date: Optional[date] = None) -> list:
        today = from_date or datetime.today().date()
        return [
            tx for tx in self.transactions
            if tx.get("due_date") and datetime.fromisoformat(tx["due_date"]).date() >= today and not tx.get("paid", False)
        ]

    def get_monthly_summary(self, month: int = None, year: int = None) -> Dict[str, float]:
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        monthly_transactions = [
            t for t in self.transactions
            if t.get("due_date") and datetime.fromisoformat(t["due_date"]).month == month and
               datetime.fromisoformat(t["due_date"]).year == year and not t.get("paid", False)
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
    finance_data = HomeFinanceData(hass)
    hass.data[DOMAIN] = finance_data

    await finance_data.async_load()

    domain_config = config.get(DOMAIN, {})

    for account_config in domain_config.get("accounts", []):
        await finance_data.add_account(
            account_config["name"],
            account_config["type"],
            account_config.get("initial_balance", 0)
        )

    for category_config in domain_config.get("categories", []):
        finance_data.categories[category_config["name"]] = {
            "type": category_config["type"],
            "budget_limit": category_config.get("budget_limit")
        }

    async def add_transaction_service(call: ServiceCall):
        due_date = call.data.get("due_date")
        if isinstance(due_date, str):
            due_date = dt_util.parse_date(due_date)

        success = await finance_data.add_transaction(
            call.data.get("account"),
            call.data.get("amount"),
            call.data.get("description"),
            call.data.get("category", "Geral"),
            call.data.get("type", "expense"),
            due_date
        )

        if success:
            hass.bus.async_fire(f"{DOMAIN}_transaction_added", {
                "account": call.data.get("account"),
                "amount": call.data.get("amount"),
                "description": call.data.get("description"),
                "due_date": str(due_date) if due_date else None
            })
            async_dispatcher_send(hass, "home_finance_update_sensors")

    async def add_account_service(call: ServiceCall):
        await finance_data.add_account(
            call.data.get("name"),
            call.data.get("type"),
            call.data.get("initial_balance", 0)
        )
        hass.bus.async_fire(f"{DOMAIN}_account_added", {
            "name": call.data.get("name"),
            "type": call.data.get("type")
        })
        async_dispatcher_send(hass, "home_finance_update_sensors")

    async def reset_transactions_service(call: ServiceCall):
        await finance_data.reset_transactions()
        hass.bus.async_fire(f"{DOMAIN}_transactions_reset", {})
        async_dispatcher_send(hass, "home_finance_update_sensors")

    async def mark_transaction_paid_service(call: ServiceCall):
        tx_id = call.data.get("transaction_id")
        success = await finance_data.mark_transaction_paid(tx_id)
        if success:
            hass.bus.async_fire(f"{DOMAIN}_transaction_paid", {"id": tx_id})
            async_dispatcher_send(hass, "home_finance_update_sensors")
        else:
            _LOGGER.warning(f"Transação {tx_id} não encontrada")

    hass.services.async_register(
        DOMAIN, "add_transaction", add_transaction_service,
        schema=vol.Schema({
            vol.Required("account"): str,
            vol.Required("amount"): vol.Coerce(float),
            vol.Required("description"): str,
            vol.Optional("category", default="Geral"): str,
            vol.Optional("type", default="expense"): vol.In(["income", "expense"]),
            vol.Optional("due_date"): cv.date
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

    hass.services.async_register(
        DOMAIN, "reset_transactions", reset_transactions_service
    )

    hass.services.async_register(
        DOMAIN, "mark_transaction_paid", mark_transaction_paid_service,
        schema=vol.Schema({
            vol.Required("transaction_id"): vol.Coerce(int)
        })
    )

    await discovery.async_load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)
    return True
