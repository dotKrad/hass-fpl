from homeassistant import const
from datetime import datetime, timedelta
from .fplapi import FplApi
import aiohttp
import asyncio
from homeassistant.helpers.entity import Entity
from homeassistant import util

from homeassistant.const import CONF_NAME, EVENT_CORE_CONFIG_UPDATE
from .const import DOMAIN, ICON

MIN_TIME_BETWEEN_SCANS = timedelta(minutes=1440)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1440)


def setup(hass, config):
    return True


def setup_platform(hass, config, add_devices, discovery_info=None):
    setup(hass, config)
    add_devices([FplSensor(hass, config)])


async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([FplSensor(hass, config_entry.data)])


class FplSensor(Entity):
    def __init__(self, hass, config):
        self._config = config
        self.username = config.get(const.CONF_USERNAME)
        self.password = config.get(const.CONF_PASSWORD)
        self._state = 0
        self.loop = hass.loop
        self.api = None

    async def _core_config_updated(self, _event):
        """Handle core config updated."""
        print("Core config updated")
        # self._init_data()
        # if self._unsub_fetch_data:
        #    self._unsub_fetch_data()
        #    self._unsub_fetch_data = None
        # await self._fetch_data()

    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def name(self):
        name = self._config.get(CONF_NAME)
        if name is not None:
            return f"{DOMAIN.upper()} {name}"

        return DOMAIN

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def state_attributes(self):
        return {
            # "yesterday_kwh": self.api.yesterday_kwh,
            # "yesterday_dollars": self.api.yesterday_dollars.replace("$", ""),
            "mtd_kwh": self.api.mtd_kwh,
            "mtd_dollars": self.api.mtd_dollars.replace("$", ""),
            "projected_bill": self.api.projected_bill,
        }

    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        session = aiohttp.ClientSession()
        api = FplApi(self.username, self.password, True, self.loop, session)
        await api.login()
        # await api.async_get_yesterday_usage()
        await api.async_get_mtd_usage()
        await session.close()

        self._state = api.projected_bill
        self.api = api
