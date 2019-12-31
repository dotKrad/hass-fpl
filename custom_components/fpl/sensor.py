from homeassistant import const
from datetime import datetime, timedelta
from .fplapi import FplApi
import aiohttp
import asyncio
from homeassistant.helpers.entity import Entity
from homeassistant import util

from homeassistant.const import CONF_NAME, EVENT_CORE_CONFIG_UPDATE
from .const import DOMAIN, ICON, LOGIN_RESULT_OK

MIN_TIME_BETWEEN_SCANS = timedelta(minutes=1440)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1440)


def setup(hass, config):
    return True


async def async_setup_entry(hass, config_entry, async_add_entities):
    username = config_entry.data.get(const.CONF_USERNAME)
    password = config_entry.data.get(const.CONF_PASSWORD)

    session = aiohttp.ClientSession()
    try:
        api = FplApi(username, password, hass.loop, session)
        result = await api.login()

        if result == LOGIN_RESULT_OK:
            accounts = await api.async_get_open_accounts()
            for account in accounts:
                async_add_entities([FplSensor(hass, config_entry.data, account)])
            pass

    except Exception:  # pylint: disable=broad-except
        pass

    await session.close()


class FplSensor(Entity):
    def __init__(self, hass, config, account):
        self._config = config
        self.username = config.get(const.CONF_USERNAME)
        self.password = config.get(const.CONF_PASSWORD)
        self._state = 0
        self.loop = hass.loop

        self._account = account
        self._data = None

    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return "{}{}".format(self._account, hash(self._account))

    @property
    def name(self):
        return f"{DOMAIN.upper()} {self._account}"

    @property
    def state(self):
        return self._data["bill_to_date"]

    @property
    def unit_of_measurement(self):
        return ""

    @property
    def icon(self):
        return ICON

    @property
    def state_attributes(self):
        return self._data

    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        session = aiohttp.ClientSession()
        try:
            api = FplApi(self.username, self.password, self.loop, session)
            await api.login()
            self._data = await api.async_get_data(self._account)

        except Exception:  # pylint: disable=broad-except
            pass

        await session.close()
