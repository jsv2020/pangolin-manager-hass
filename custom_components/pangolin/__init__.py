"""Pangolin resource switches."""
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import PangolinClient
from .coordinator import PangolinCoordinator

async def async_setup_entry(hass, entry):
    client = PangolinClient(async_get_clientsession(hass), entry.data["url"],
        entry.data["api_key"], entry.data["org_id"])
    coordinator = PangolinCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SWITCH])
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, [Platform.SWITCH])
