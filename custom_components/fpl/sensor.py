import logging
from datetime import datetime, timedelta
from .fplapi import FplApi
import aiohttp
import asyncio
from homeassistant.helpers.entity import Entity
from homeassistant import util

from homeassistant.helpers.event import async_call_later

from homeassistant.const import (
    CONF_NAME,
    EVENT_CORE_CONFIG_UPDATE,
    STATE_UNKNOWN,
    CONF_USERNAME,
    CONF_PASSWORD,
    STATE_UNKNOWN,
)
from .const import DOMAIN, ICON, LOGIN_RESULT_OK

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_SCANS = timedelta(minutes=30)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)


def setup(hass, config):
    return True


async def async_setup_entry(hass, config_entry, async_add_entities):
    username = config_entry.data.get(CONF_USERNAME)
    password = config_entry.data.get(CONF_PASSWORD)

    session = aiohttp.ClientSession()
    try:
        api = FplApi(username, password, hass.loop, session)
        result = await api.login()

        fpl_accounts = []

        if result == LOGIN_RESULT_OK:
            accounts = await api.async_get_open_accounts()
            for account in accounts:
                _LOGGER.info(f"Adding fpl account: {account}")
                fpl_accounts.append(FplSensor(hass, config_entry.data, account))

            async_add_entities(fpl_accounts)
    except Exception as e:  # pylint: disable=broad-except
        _LOGGER.error(f"Adding fpl accounts: {str(e)}")
        async_call_later(
            hass, 15, async_setup_entry(hass, config_entry, async_add_entities)
        )

    await session.close()


class FplSensor(Entity):
    def __init__(self, hass, config, account):
        self._config = config
        self.username = config.get(CONF_USERNAME)
        self.password = config.get(CONF_PASSWORD)
        self._state = STATE_UNKNOWN
        self.loop = hass.loop

        self._account = account
        self._data = None

    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def unique_id(self):
        """Return the ID of this device."""
        id = "{}{}".format(DOMAIN, self._account)
        return id

    @property
    def name(self):
        return f"{DOMAIN.upper()} {self._account}"

    @property
    def state(self):
        state = self._state
        data = self._data

        if type(data) is dict:
            if "budget_bill" in data.keys():
                if data["budget_bill"]:
                    if "projected_budget_bill" in data.keys():
                        state = data["projected_budget_bill"]
            else:
                if "projected_bill" in data.keys():
                    state = data["projected_bill"]

        return state

    # @property
    # def unit_of_measurement(self):
    #    return "$"

    @property
    def icon(self):
        return ICON

    @property
    def state_attributes(self):
        return self._data

    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        try:
            session = aiohttp.ClientSession()
            api = FplApi(self.username, self.password, self.loop, session)
            await api.login()
            data = await api.async_get_data(self._account)
            if data != {}:
                self._data = data

        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.warning(f"Error ocurred during update: { str(e)}")

        finally:
            await session.close()
