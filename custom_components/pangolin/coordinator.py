"""Shared polling for all resource switches."""
from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from .api import PangolinError, PangolinAuthError

class PangolinCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, client):
        super().__init__(hass, logging.getLogger(__name__), name="Pangolin",
            config_entry=entry, update_interval=timedelta(seconds=30))
        self.client = client

    async def _async_update_data(self):
        try:
            return await self.client.resources()
        except PangolinAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except PangolinError as err:
            raise UpdateFailed(str(err)) from err
