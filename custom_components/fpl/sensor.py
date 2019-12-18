from homeassistant import const
from datetime import datetime, timedelta
from .fplapi import FplApi
import aiohttp
import asyncio
from homeassistant.helpers.entity import Entity
from homeassistant import util

MIN_TIME_BETWEEN_SCANS = timedelta(minutes=1440)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1440)


def setup(hass, config):
    return True


def setup_platform(hass, config, add_devices, discovery_info=None):
    setup(hass, config)
    add_devices([FplSensor(hass, config)])


class FplSensor(Entity):
    def __init__(self, hass, config):
        print("init")
        self.username = config.get(const.CONF_USERNAME)
        self.password = config.get(const.CONF_PASSWORD)
        self._state = 0
        self.loop = hass.loop
        self.api = None

    @property
    def name(self):
        """Returns the name of the sensor."""
        return "fpl"

    @property
    def state(self):
        return self._state

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
