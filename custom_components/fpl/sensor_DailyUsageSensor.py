"""Daily Usage Sensors"""
from datetime import timedelta, datetime
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from .fplEntity import FplEnergyEntity, FplMoneyEntity


class FplDailyUsageSensor(FplMoneyEntity):
    """Daily Usage Cost Sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage")

    @property
    def native_value(self):
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "cost" in data[-1].keys():
            self._attr_native_value = data[-1]["cost"]

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")
        attributes = {}
        # attributes["state_class"] = SensorStateClass.TOTAL_INCREASING
        if data is not None and len(data) > 0 and "readTime" in data[-1].keys():
            attributes["date"] = data[-1]["readTime"]

        return attributes


class FplDailyUsageKWHSensor(FplEnergyEntity):
    """Daily Usage Kwh Sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage KWH")

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    @property
    def native_value(self):
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "usage" in data[-1].keys():
            self._attr_native_value = data[-1]["usage"]

        return self._attr_native_value

    @property
    def last_reset(self) -> datetime | None:
        data = self.getData("daily_usage")
        if data is not None and len(data) > 0 and "usage" in data[-1].keys():
            date = data[-1]["readTime"]
            _attr_last_reset = date - timedelta(days=1)
        else:
            _attr_last_reset = None

        return _attr_last_reset

    def customAttributes(self):
        """Return the state attributes."""
        # data = self.getData("daily_usage")
        # date = data[-1]["readTime"]
        # last_reset = date - timedelta(days=1)

        attributes = {}
        # attributes["state_class"] = SensorStateClass.TOTAL_INCREASING
        # attributes["date"] = date
        # attributes["last_reset"] = last_reset
        return attributes


class FplDailyReceivedKWHSensor(FplEnergyEntity):
    """daily received Kwh sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Received KWH")

    # _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "netReceivedKwh" in data[-1].keys():
            self._attr_native_value = data[-1]["netReceivedKwh"]

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")
        attributes = {}

        if data is not None and len(data) > 0 and "readTime" in data[-1].keys():
            date = data[-1]["readTime"]
            # last_reset = date - timedelta(days=1)
            attributes["date"] = date
            # attributes["last_reset"] = last_reset
        return attributes


class FplDailyDeliveredKWHSensor(FplEnergyEntity):
    """daily delivered Kwh sensor"""

    # _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Delivered KWH")

    @property
    def native_value(self):
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "netDeliveredKwh" in data[-1].keys():
            self._attr_native_value = data[-1]["netDeliveredKwh"]

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")
        attributes = {}
        if data is not None and len(data) > 0 and "readTime" in data[-1].keys():
            date = data[-1]["readTime"]
            # last_reset = date - timedelta(days=1)
            attributes["date"] = date
            # attributes["last_reset"] = last_reset
        return attributes
