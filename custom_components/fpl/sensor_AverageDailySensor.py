"""Average daily sensors"""
from .fplEntity import FplMoneyEntity

from homeassistant.components.sensor import SensorStateClass

class DailyAverageSensor(FplMoneyEntity):
    """average daily sensor, use budget value if available, otherwise use actual daily values"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average")

    @property
    def native_value(self):
        daily_avg = self.getData("daily_avg")

        if daily_avg is not None:
            self._attr_native_value = daily_avg

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = SensorStateClass.TOTAL
        return attributes


class BudgetDailyAverageSensor(FplMoneyEntity):
    """budget daily average sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Budget Daily Average")

    @property
    def native_value(self):
        budget_billing_daily_avg = self.getData("budget_billing_daily_avg")

        if budget_billing_daily_avg is not None:
            self._attr_native_value = budget_billing_daily_avg

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = SensorStateClass.TOTAL
        return attributes


class ActualDailyAverageSensor(FplMoneyEntity):
    """Actual daily average sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Actual Daily Average")

    @property
    def native_value(self):
        daily_avg = self.getData("daily_avg")

        if daily_avg is not None:
            self._attr_native_value = daily_avg

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = SensorStateClass.TOTAL
        return attributes
