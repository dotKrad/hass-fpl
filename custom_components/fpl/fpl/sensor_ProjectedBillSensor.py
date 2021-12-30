from .fplEntity import FplEntity


class FplProjectedBillSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Bill")

    @property
    def state(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

        if budget == True and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_projected_bill")

        return self.getData("projected_bill")

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Projected Bill"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes

    @property
    def icon(self):
        return "mdi:currency-usd"


# Defered Amount
class DeferedAmountSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Defered Amount")

    @property
    def state(self):
        if self.getData("defered_amount") is not None:
            return self.getData("defered_amount")
        return 0

    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Defered Amount"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes


class ProjectedBudgetBillSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Budget Bill")

    @property
    def state(self):
        return self.getData("budget_billing_projected_bill")

    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Projected Budget Bill"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes['unit_of_measurement'] = "$"
        return attributes


class ProjectedActualBillSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Actual Bill")

    @property
    def state(self):
        return self.getData("projected_bill")

    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Projected Actual Bill"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes['unit_of_measurement'] = "$"
        
        return attributes
