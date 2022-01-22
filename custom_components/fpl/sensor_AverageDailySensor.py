"""Average daily sensors"""
from .fplEntity import FplMoneyEntity


class DailyAverageSensor(FplMoneyEntity):
    """average daily sensor, use budget value if available, otherwise use actual daily values"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average")

    @property
    def state(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_daily_avg")

        if budget and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_daily_avg")

        return self.getData("daily_avg")

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = "total"
        return attributes


class BudgetDailyAverageSensor(FplMoneyEntity):
    """budget daily average sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Budget Daily Average")

    @property
    def state(self):
        return self.getData("budget_billing_daily_avg")

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = "total"
        return attributes


class ActualDailyAverageSensor(FplMoneyEntity):
    """Actual daily average sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Actual Daily Average")

    @property
    def state(self):
        return self.getData("daily_avg")

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = "total"
        return attributes
