"""UI configuration and API key renewal."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .api import PangolinClient, PangolinError, PangolinAuthError, normalize_url

class PangolinConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                user_input["url"] = normalize_url(user_input["url"])
                user_input["org_id"] = user_input["org_id"].strip()
                user_input["api_key"] = user_input["api_key"].strip()
                await PangolinClient(async_get_clientsession(self.hass), user_input["url"],
                    user_input["api_key"], user_input["org_id"]).resources()
            except ValueError:
                errors["base"] = "invalid_url"
            except PangolinAuthError:
                errors["base"] = "invalid_auth"
            except PangolinError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input["url"] + "|" + user_input["org_id"])
                if self.source == "reauth":
                    self._abort_if_unique_id_mismatch()
                    return self.async_update_reload_and_abort(self._get_reauth_entry(), data_updates=user_input)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Pangolin · " + user_input["org_id"], data=user_input)
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required("url"): str,
            vol.Required("org_id"): str,
            vol.Required("api_key"): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
        }), errors=errors)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_user()
