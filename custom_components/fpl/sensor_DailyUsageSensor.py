"""Daily Usage Sensors"""
from datetime import timedelta, datetime
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_TOTAL,
    DEVICE_CLASS_ENERGY,
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
            return data[-1]["cost"]

        return None

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL_INCREASING
        if data is not None and len(data) > 0 and "readTime" in data[-1].keys():
            attributes["date"] = data[-1]["readTime"]

        return attributes


class FplDailyUsageKWHSensor(FplEnergyEntity):
    """Daily Usage Kwh Sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage KWH")

    _attr_state_class = STATE_CLASS_TOTAL_INCREASING
    _attr_device_class = DEVICE_CLASS_ENERGY

    @property
    def native_value(self):
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "usage" in data[-1].keys():
            return data[-1]["usage"]

        return None

    @property
    def last_reset(self) -> datetime | None:
        data = self.getData("daily_usage")
        date = data[-1]["readTime"]
        last_reset = date - timedelta(days=1)
        return last_reset

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")
        date = data[-1]["readTime"]
        last_reset = date - timedelta(days=1)

        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL_INCREASING
        attributes["date"] = date
        # attributes["last_reset"] = last_reset
        return attributes


class FplDailyReceivedKWHSensor(FplEnergyEntity):
    """daily received Kwh sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Received KWH")

    # _attr_state_class = STATE_CLASS_TOTAL_INCREASING

    @property
    def native_value(self):
        data = self.getData("daily_usage")
        if data is not None and len(data) > 0 and "netReceivedKwh" in data[-1].keys():
            return data[-1]["netReceivedKwh"]
        return 0

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")
        date = data[-1]["readTime"]
        last_reset = date - timedelta(days=1)

        attributes = {}
        attributes["date"] = date
        # attributes["last_reset"] = last_reset
        return attributes


class FplDailyDeliveredKWHSensor(FplEnergyEntity):
    """daily delivered Kwh sensor"""

    # _attr_state_class = STATE_CLASS_TOTAL_INCREASING

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Delivered KWH")

    @property
    def native_value(self):
        data = self.getData("daily_usage")
        if data is not None and len(data) > 0 and "netDeliveredKwh" in data[-1].keys():
            return data[-1]["netDeliveredKwh"]
        return 0

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")
        date = data[-1]["readTime"]
        last_reset = date - timedelta(days=1)

        attributes = {}
        attributes["date"] = date
        # attributes["last_reset"] = last_reset
        return attributes
