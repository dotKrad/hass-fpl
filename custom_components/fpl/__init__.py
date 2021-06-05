""" FPL Component """


import logging
import asyncio

from datetime import timedelta
from homeassistant.core import Config, HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle

from .fplapi import FplApi
from .const import (
    DOMAIN,
    DOMAIN_DATA,
    CONF_USERNAME,
    CONF_PASSWORD,
    PLATFORMS,
    STARTUP_MESSAGE,
)
from .fplDataUpdateCoordinator import FplDataUpdateCoordinator

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__package__)


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


async def async_setup_entry(hass, entry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    # Get "global" configuration.
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    # Configure the client.
    _LOGGER.info(f"Configuring the client")
    session = async_get_clientsession(hass)
    client = FplApi(username, password, session)

    coordinator = FplDataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    """Set up Fpl as config entry."""

    entry.add_update_listener(async_reload_entry)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded
