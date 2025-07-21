"""Sensores para Home Finance."""
import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Configura os sensores do Home Finance."""

    finance_data = hass.data.get("home_finance")
    if not finance_data:
        _LOGGER.error("Dados do Home Finance não encontrados")
        return

    sensors: list[SensorEntity] = []

    """ Sensores de saldo para cada conta """
    for account_name in finance_data.accounts:
        sensors.append(AccountBalanceSensor(finance_data, account_name))

    """ Sensores de resumo mensal e total """
    sensors.extend([
        MonthlyIncomeSensor(finance_data),
        MonthlyExpenseSensor(finance_data),
        MonthlyBalanceSensor(finance_data),
        TotalBalanceSensor(finance_data),
        NextDueTransactionSensor(finance_data),
        UpcomingTransactionsListSensor(finance_data),
    ])

    """ Sensor individual para cada transação futura não paga """
    for tx in finance_data.transactions:
        if tx.get("due_date") and not tx.get("paid", False):
            try:
                tx_date = datetime.fromisoformat(tx["due_date"]).date()
                if tx_date >= datetime.now().date():
                    sensors.append(DueTransactionSensor(tx))
            except Exception as e:
                _LOGGER.warning(f"Erro ao criar sensor da transação: {e}")

    async_add_entities(sensors, True)

class FinanceBaseSensor(SensorEntity):
    """Sensor base para Home Finance."""

    _attr_should_poll = True

    def __init__(self, finance_data, name: str):
        self._finance_data = finance_data
        self._name = name
        self._state = None
        self._attributes = {}

    @property
    def name(self) -> str:
        return f"Home Finance {self._name}"

    @property
    def unique_id(self) -> str:
        return f"home_finance_{self._name.lower().replace(' ', '_')}"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    @property
    def unit_of_measurement(self) -> str:
        return "R$"

class AccountBalanceSensor(FinanceBaseSensor):
    def __init__(self, finance_data, account_name: str):
        super().__init__(finance_data, f"Saldo {account_name}")
        self._account_name = account_name

    @property
    def icon(self) -> str:
        account_type = self._finance_data.accounts[self._account_name]["type"]
        icons = {
            "conta_corrente": "mdi:bank",
            "poupanca": "mdi:piggy-bank",
            "investimento": "mdi:chart-line",
            "cartao": "mdi:credit-card"
        }
        return icons.get(account_type, "mdi:wallet")

    def update(self) -> None:
        account = self._finance_data.accounts.get(self._account_name)
        if account:
            self._state = account["balance"]
            self._attributes = {
                "account_type": account["type"],
                "initial_balance": account["initial_balance"],
                "created_at": account["created_at"],
            }

class MonthlyIncomeSensor(FinanceBaseSensor):
    def __init__(self, finance_data):
        super().__init__(finance_data, "Receitas Mensais")

    @property
    def icon(self) -> str:
        return "mdi:cash-plus"

    def update(self) -> None:
        summary = self._finance_data.get_monthly_summary()
        self._state = summary["income"]
        self._attributes = {
            "month": datetime.now().month,
            "year": datetime.now().year,
            "transactions_count": summary["transactions_count"],
        }

class MonthlyExpenseSensor(FinanceBaseSensor):
    def __init__(self, finance_data):
        super().__init__(finance_data, "Despesas Mensais")

    @property
    def icon(self) -> str:
        return "mdi:cash-minus"

    def update(self) -> None:
        summary = self._finance_data.get_monthly_summary()
        self._state = summary["expenses"]
        self._attributes = {
            "month": datetime.now().month,
            "year": datetime.now().year,
            "transactions_count": summary["transactions_count"],
        }

class MonthlyBalanceSensor(FinanceBaseSensor):
    def __init__(self, finance_data):
        super().__init__(finance_data, "Saldo Mensal")

    @property
    def icon(self) -> str:
        return "mdi:scale-balance"

    def update(self) -> None:
        summary = self._finance_data.get_monthly_summary()
        self._state = summary["balance"]
        self._attributes = {
            "income": summary["income"],
            "expenses": summary["expenses"],
            "month": datetime.now().month,
            "year": datetime.now().year,
        }

class TotalBalanceSensor(FinanceBaseSensor):
    def __init__(self, finance_data):
        super().__init__(finance_data, "Saldo Total")

    @property
    def icon(self) -> str:
        return "mdi:cash-multiple"

    def update(self) -> None:
        total = sum(
            account["balance"] for account in self._finance_data.accounts.values()
        )
        self._state = total
        self._attributes = {
            "accounts_count": len(self._finance_data.accounts),
            "accounts": list(self._finance_data.accounts.keys()),
        }

class NextDueTransactionSensor(FinanceBaseSensor):
    def __init__(self, finance_data):
        super().__init__(finance_data, "Próximo Vencimento")

    @property
    def icon(self) -> str:
        return "mdi:calendar-clock"

    def update(self) -> None:
        future_due = [
            t for t in self._finance_data.transactions
            if t.get("due_date")
            and datetime.fromisoformat(t["due_date"]).date() >= datetime.now().date()
            and not t.get("paid", False)
        ]
        if future_due:
            future_due.sort(key=lambda t: datetime.fromisoformat(t["due_date"]).date())
            next_tx = future_due[0]
            self._state = next_tx["due_date"]
            self._attributes = {
                "description": next_tx["description"],
                "amount": next_tx["amount"],
                "account": next_tx["account"],
                "category": next_tx["category"],
                "type": next_tx["type"],
            }
        else:
            self._state = "Sem vencimentos futuros"
            self._attributes = {}

class UpcomingTransactionsListSensor(FinanceBaseSensor):
    def __init__(self, finance_data):
        super().__init__(finance_data, "Lista de Vencimentos")

    @property
    def icon(self) -> str:
        return "mdi:calendar-text"

    @property
    def unit_of_measurement(self) -> str | None:
        return None  # Remover "R$"

    def update(self) -> None:
        future_due = [
            t for t in self._finance_data.transactions
            if t.get("due_date")
            and datetime.fromisoformat(t["due_date"]).date() >= datetime.now().date()
            and not t.get("paid", False)
        ]
        future_due.sort(key=lambda t: datetime.fromisoformat(t["due_date"]).date())
        self._state = len(future_due)
        self._attributes = {
            f"{t['due_date']} - {t['description']}": {
                "id": t["id"],
                "amount": t["amount"],
                "account": t["account"],
                "category": t["category"],
                "type": t["type"],
                "paid": t.get("paid", False)
            }
            for t in future_due
        }

class DueTransactionSensor(SensorEntity):
    def __init__(self, tx):
        self._tx = tx
        self._attr_name = f"{tx['description']} ({tx['due_date']})"
        self._attr_unique_id = f"home_finance_tx_{tx['id']}"
        self._attr_icon = "mdi:calendar-alert"

    @property
    def state(self):
        return self._tx["amount"]

    @property
    def unit_of_measurement(self):
        return "R$"

    @property
    def extra_state_attributes(self):
        return {
            "description": self._tx["description"],
            "account": self._tx["account"],
            "category": self._tx["category"],
            "due_date": self._tx["due_date"],
            "paid": self._tx["paid"],
            "type": self._tx["type"],
        }
