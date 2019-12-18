from collections import OrderedDict

import voluptuous as vol
from .fplapi import FplApi
from homeassistant import config_entries
import aiohttp
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
from homeassistant.core import callback


@callback
def configured_instances(hass):
    """Return a set of configured SimpliSafe instances."""
    entites = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        entites.append(f"{entry.data.get(CONF_USERNAME)}")
    return set(entites)


class FplFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """Handle a flow initialized by the user."""
        self._errors = {}

        # if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")
        # if self.hass.data.get(DOMAIN):
        #    return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            if username not in configured_instances(self.hass):
                valid = await self._test_credentials(username, password)

                if valid:
                    return self.async_create_entry(
                        title=user_input[CONF_NAME], data=user_input
                    )
                else:
                    self._errors["base"] = "auth"
            else:
                self._errors[CONF_NAME] = "name_exists"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""

        # Defaults
        username = ""
        password = ""
        name = "Home"

        if user_input is not None:
            if CONF_USERNAME in user_input:
                username = user_input[CONF_USERNAME]
            if CONF_PASSWORD in user_input:
                password = user_input[CONF_PASSWORD]
            if CONF_NAME in user_input:
                name = user_input[CONF_NAME]

        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_NAME, default=name)] = str
        data_schema[vol.Required(CONF_USERNAME, default=username)] = str
        data_schema[vol.Required(CONF_PASSWORD, default=password)] = str

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def _test_credentials(self, username, password):
        """Return true if credentials is valid."""
        try:
            session = aiohttp.ClientSession()
            api = FplApi(username, password, True, None, session)
            await api.login()
            return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False
