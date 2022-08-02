"""energy sensors"""
from datetime import date, timedelta
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_TOTAL,
)
from .fplEntity import FplEnergyEntity


class ProjectedKWHSensor(FplEnergyEntity):
    """Projected KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected KWH")

    @property
    def native_value(self):
        return self.getData("projectedKWH")

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes


class DailyAverageKWHSensor(FplEnergyEntity):
    """Daily Average KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average KWH")

    @property
    def native_value(self):
        return self.getData("dailyAverageKWH")

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes


class BillToDateKWHSensor(FplEnergyEntity):
    """Bill To Date KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Bill To Date KWH")

    @property
    def native_value(self):
        return self.getData("billToDateKWH")

    def customAttributes(self):
        """Return the state attributes."""

        # data = self.getData("daily_usage")
        # date = data[-1]["readTime"]
        asOfDays = self.getData("as_of_days")
        last_reset = date.today() - timedelta(days=asOfDays)

        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL_INCREASING
        # attributes["last_reset"] = last_reset
        return attributes


class NetReceivedKWHSensor(FplEnergyEntity):
    """Received Meter Reading KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Received Meter Reading KWH")

    @property
    def native_value(self):
        return self.getData("recMtrReading")

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL_INCREASING
        return attributes


class NetDeliveredKWHSensor(FplEnergyEntity):
    """Delivered Meter Reading KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Delivered Meter Reading KWH")

    @property
    def native_value(self):
        return self.getData("delMtrReading")

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL_INCREASING
        return attributes
