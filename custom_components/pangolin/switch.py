"""One switch per public or private Pangolin resource."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.exceptions import HomeAssistantError
from .api import PangolinError

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    known = set()
    def discover():
        fresh = set(coordinator.data) - known
        known.update(fresh)
        async_add_entities(PangolinSwitch(coordinator, entry, key) for key in sorted(fresh))
    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))

class PangolinSwitch(CoordinatorEntity, SwitchEntity):
    _attr_icon = "mdi:server-network"
    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        self.key = key
        self._attr_unique_id = f"{entry.unique_id}:{key}"
        self._attr_name = coordinator.data[key].get("name", key)

    @property
    def available(self):
        return super().available and self.key in self.coordinator.data

    @property
    def is_on(self):
        row = self.coordinator.data.get(self.key)
        return row["enabled"] if row else None

    async def _set(self, enabled):
        row = self.coordinator.data.get(self.key)
        if row is None:
            raise HomeAssistantError("Resource is no longer available")
        try:
            await self.coordinator.client.set_enabled(row, enabled)
        except PangolinError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self._set(True)

    async def async_turn_off(self, **kwargs):
        await self._set(False)
