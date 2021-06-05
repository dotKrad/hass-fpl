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
        try:
            if self.getData("budget_bill") == True:
                attributes["budget_bill"] = self.getData("budget_bill")
        except:
            pass

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
        if self.getData("budget_bill") == True:
            return self.getData("defered_amount")
        return 0

    @property
    def icon(self):
        return "mdi:currency-usd"


class ProjectedBudgetBillSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Budget Bill")

    @property
    def state(self):
        return self.getData("budget_billing_projected_bill")

    @property
    def icon(self):
        return "mdi:currency-usd"


class ProjectedActualBillSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Actual Bill")

    @property
    def state(self):
        return self.getData("projected_bill")

    @property
    def icon(self):
        return "mdi:currency-usd"
