from .fplEntity import FplEntity


class FplAverageDailySensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average")

    @property
    def state(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_daily_avg")

        if budget == True and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_daily_avg")

        return self.getData("daily_avg")

    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Daily Average"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes

class BudgetDailyAverageSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Budget Daily Average")

    @property
    def state(self):
        return self.getData("budget_billing_daily_avg")

    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Budget Daily Average"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes

