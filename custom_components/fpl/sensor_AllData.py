from .fplEntity import FplEntity


class AllDataSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "")

    @property
    def state(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

        if budget == True and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_projected_bill")

        return self.getData("projected_bill")

    def defineAttributes(self):
        """Return the state attributes."""
        return self.coordinator.data.get(self.account)

    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Budget Projected Bill"
        attributes["device_class"] = "monetary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes