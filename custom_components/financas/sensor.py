"""Sensor do Organizador Financeiro."""

from homeassistant.helpers.entity import Entity
from .const import DOMAIN


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the finance sensor platform."""
    async_add_entities([FinanceSensor()])


class FinanceSensor(Entity):
    """Representa um sensor financeiro."""

    def __init__(self):
        self._state = "OK"
        self._attr_name = "Saldo Financeiro"
        self._attr_icon = "mdi:currency-usd"

    @property
    def state(self):
        return self._state

    def update(self):
        self._state = "R$ 0,00"
