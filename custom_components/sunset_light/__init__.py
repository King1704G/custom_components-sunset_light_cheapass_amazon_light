
"""The Sunset Light integration."""
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sunset Light from a config entry."""
    _LOGGER.info(
        "Setting up Sunset Light entry: id=%s title=%s data=%s",
        entry.entry_id,
        entry.title,
        entry.data,
    )
    await hass.config_entries.async_forward_entry_setups(entry, ["light"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "light")
