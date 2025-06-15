"""Organizador Financeiro - Home Assistant Integration."""

from homeassistant.core import HomeAssistant
from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Organizador Financeiro component."""
    hass.states.async_set(f"{DOMAIN}.status", "ativo")
    return True
