"""Fpl Entity class"""

from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity, STATE_CLASS_MEASUREMENT
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import (
    CURRENCY_DOLLAR,
    DEVICE_CLASS_ENERGY,
    ENERGY_KILO_WATT_HOUR,
    DEVICE_CLASS_MONETARY,
)
from .const import DOMAIN, VERSION, ATTRIBUTION


class FplEntity(CoordinatorEntity, SensorEntity):
    """FPL base entity"""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator, config_entry, account, sensorName):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.account = account
        self.sensorName = sensorName

    @property
    def unique_id(self):
        """Return the ID of this device."""
        sensorName = self.sensorName.lower().replace(" ", "")
        return f"{DOMAIN}{self.account}{sensorName}"

    @property
    def name(self):
        return f"{DOMAIN.upper()} {self.account} {self.sensorName}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.account)},
            "name": f"FPL Account {self.account}",
            "model": VERSION,
            "manufacturer": "Florida Power & Light",
        }

    def customAttributes(self) -> dict:
        """override this method to set custom attributes"""
        return {}

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = {
            #            "attribution": ATTRIBUTION,
            # "integration": "FPL",
        }
        attributes.update(self.customAttributes())
        return attributes

    def getData(self, field):
        """call this method to retrieve sensor data"""
        return self.coordinator.data.get(self.account).get(field, None)


class FplEnergyEntity(FplEntity):
    """Represents a energy sensor"""

    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = DEVICE_CLASS_ENERGY
    _attr_icon = "mdi:flash"
    _attr_state_class = STATE_CLASS_MEASUREMENT

    @property
    def last_reset(self) -> datetime:
        """Return the time when the sensor was last reset, if any."""

        today = datetime.today()
        yesterday = today - timedelta(days=1)
        return datetime.combine(yesterday, datetime.min.time())


class FplMoneyEntity(FplEntity):
    """Represents a money sensor"""

    _attr_native_unit_of_measurement = CURRENCY_DOLLAR
    _attr_device_class = DEVICE_CLASS_MONETARY
    _attr_icon = "mdi:currency-usd"


class FplDateEntity(FplEntity):
    """Represents a date or days"""

    _attr_icon = "mdi:calendar"


class FplDayEntity(FplEntity):
    """Represents a date or days"""

    _attr_native_unit_of_measurement = "days"
    _attr_icon = "mdi:calendar"
