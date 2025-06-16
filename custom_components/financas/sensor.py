"""Sensores para Home Finance."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CURRENCY_REAL
from homeassistant.core import HomeAssistant, callback
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
    
    sensors = []
    
    # Sensores de saldo para cada conta
    for account_name in finance_data.accounts:
        sensors.append(AccountBalanceSensor(finance_data, account_name))
    
    # Sensores de resumo mensal
    sensors.extend([
        MonthlyIncomeSensor(finance_data),
        MonthlyExpenseSensor(finance_data),
        MonthlyBalanceSensor(finance_data),
        TotalBalanceSensor(finance_data),
    ])
    
    async_add_entities(sensors, True)

class FinanceBaseSensor(SensorEntity):
    """Sensor base para Home Finance."""
    
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
    def state(self) -> Any:
        return self._state
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attributes
        
    @property
    def unit_of_measurement(self) -> str:
        return CURRENCY_REAL

class AccountBalanceSensor(FinanceBaseSensor):
    """Sensor de saldo da conta."""
    
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
        """Atualiza o sensor."""
        if self._account_name in self._finance_data.accounts:
            account = self._finance_data.accounts[self._account_name]
            self._state = account["balance"]
            self._attributes = {
                "account_type": account["type"],
                "initial_balance": account["initial_balance"],
                "created_at": account["created_at"].isoformat(),
            }

class MonthlyIncomeSensor(FinanceBaseSensor):
    """Sensor de receitas mensais."""
    
    def __init__(self, finance_data):
        super().__init__(finance_data, "Receitas Mensais")
        
    @property
    def icon(self) -> str:
        return "mdi:cash-plus"
        
    def update(self) -> None:
        """Atualiza o sensor."""
        summary = self._finance_data.get_monthly_summary()
        self._state = summary["income"]
        self._attributes = {
            "month": datetime.now().month,
            "year": datetime.now().year,
            "transactions_count": len([
                t for t in self._finance_data.transactions 
                if t["type"] == "income" and 
                t["date"].month == datetime.now().month and
                t["date"].year == datetime.now().year
            ])
        }

class MonthlyExpenseSensor(FinanceBaseSensor):
    """Sensor de despesas mensais."""
    
    def __init__(self, finance_data):
        super().__init__(finance_data, "Despesas Mensais")
        
    @property
    def icon(self) -> str:
        return "mdi:cash-minus"
        
    def update(self) -> None:
        """Atualiza o sensor."""
        summary = self._finance_data.get_monthly_summary()
        self._state = summary["expenses"]
        self._attributes = {
            "month": datetime.now().month,
            "year": datetime.now().year,
            "transactions_count": len([
                t for t in self._finance_data.transactions 
                if t["type"] == "expense" and 
                t["date"].month == datetime.now().month and
                t["date"].year == datetime.now().year
            ])
        }

class MonthlyBalanceSensor(FinanceBaseSensor):
    """Sensor de saldo mensal."""
    
    def __init__(self, finance_data):
        super().__init__(finance_data, "Saldo Mensal")
        
    @property
    def icon(self) -> str:
        return "mdi:scale-balance"
        
    def update(self) -> None:
        """Atualiza o sensor."""
        summary = self._finance_data.get_monthly_summary()
        self._state = summary["balance"]
        self._attributes = {
            "income": summary["income"],
            "expenses": summary["expenses"],
            "month": datetime.now().month,
            "year": datetime.now().year,
        }

class TotalBalanceSensor(FinanceBaseSensor):
    """Sensor de saldo total."""
    
    def __init__(self, finance_data):
        super().__init__(finance_data, "Saldo Total")
        
    @property
    def icon(self) -> str:
        return "mdi:cash-multiple"
        
    def update(self) -> None:
        """Atualiza o sensor."""
        total = sum(account["balance"] for account in self._finance_data.accounts.values())
        self._state = total
        self._attributes = {
            "accounts_count": len(self._finance_data.accounts),
            "accounts": list(self._finance_data.accounts.keys()),
        }
