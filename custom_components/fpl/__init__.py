""" FPL Component """

import logging
from datetime import timedelta
from homeassistant.core import Config, HomeAssistant
from homeassistant.util import Throttle
from .fplapi import FplApi
from .const import DOMAIN_DATA, CONF_USERNAME, CONF_PASSWORD

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

from .config_flow import FplFlowHandler
from .const import DOMAIN


class FplData:
    """This class handle communication and stores the data."""

    def __init__(self, hass, client):
        """Initialize the class."""
        self.hass = hass
        self.client = client

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update_data(self):
        """Update data."""
        # This is where the main logic to update platform data goes.
        try:
            data = await self.client.get_data()
            self.hass.data[DOMAIN_DATA]["data"] = data
        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.error("Could not update data - %s", error)


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured Fpl."""
    return True


async def async_setup_entry(hass, config_entry):

    # Get "global" configuration.
    username = config_entry.data.get(CONF_USERNAME)
    password = config_entry.data.get(CONF_PASSWORD)

    # Create DATA dict
    hass.data[DOMAIN_DATA] = {}

    # Configure the client.
    _LOGGER.info(f"Configuring the client")
    client = FplApi(username, password, hass.loop)
    fplData = FplData(hass, client)

    await fplData.update_data()

    hass.data[DOMAIN_DATA]["client"] = fplData

    """Set up Fpl as config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    return True
