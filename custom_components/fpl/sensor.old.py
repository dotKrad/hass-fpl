import logging
from datetime import datetime, timedelta
from .fplapi import FplApi
import aiohttp
import asyncio
from homeassistant.helpers.entity import Entity
from homeassistant import util
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_call_later

from homeassistant.const import (
    CONF_NAME,
    EVENT_CORE_CONFIG_UPDATE,
    STATE_UNKNOWN,
    CONF_USERNAME,
    CONF_PASSWORD,
    STATE_UNKNOWN,
    ATTR_FRIENDLY_NAME,
)
from .const import DOMAIN, DOMAIN_DATA, ATTRIBUTION
from .DailyUsageSensor import FplDailyUsageSensor
from .AverageDailySensor import FplAverageDailySensor
from .ProjectedBillSensor import FplProjectedBillSensor

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_SCANS = timedelta(minutes=30)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)


def setup(hass, config):
    return True


async def async_setup_entry(hass, config_entry, async_add_entities):
    try:
        accounts = config_entry.data.get("accounts")

        fpl_accounts = []

        for account in accounts:
            _LOGGER.info(f"Adding fpl account: {account}")
            fpl_accounts.append(FplSensor(hass, config_entry.data, account))
            fpl_accounts.append(FplDailyUsageSensor(hass, config_entry.data, account))
            fpl_accounts.append(FplAverageDailySensor(hass, config_entry.data, account))
            fpl_accounts.append(
                FplProjectedBillSensor(hass, config_entry.data, account)
            )

        async_add_entities(fpl_accounts)
    except:
        raise ConfigEntryNotReady


class FplSensor(Entity):
    def __init__(self, hass, config, account):
        self._config = config
        self._state = None
        self.loop = hass.loop

        self._account = account
        self._data = None

    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._account)},
            "name": f"Account {self._account}",
            "manufacturer": "Florida Power & Light",
        }

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
        data = self._data

        if type(data) is dict:
            if "budget_bill" in data.keys():
                if data["budget_bill"]:
                    if "budget_billing_projected_bill" in data.keys():
                        self._state = data["budget_billing_projected_bill"]
            else:
                if "projected_bill" in data.keys():
                    self._state = data["projected_bill"]

        return self._state

    # @property
    # def unit_of_measurement(self):
    #    return "$"

    @property
    def icon(self):
        return "mdi:flash"

    @property
    def state_attributes(self):
        return self._data

    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        # Send update "signal" to the component
        # await self.hass.data[DOMAIN_DATA]["client"].update_data()

        # Get new data (if any)
        if "data" in self.hass.data[DOMAIN_DATA]:
            data = self.hass.data[DOMAIN_DATA]["data"][self._account]

            if data != {}:
                self._data = data
                self._data["attribution"] = ATTRIBUTION