"""Projected bill sensors"""
from .fplEntity import FplMoneyEntity


class FplProjectedBillSensor(FplMoneyEntity):
    """projected bill sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Bill")

    @property
    def state(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

        if budget and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_projected_bill")

        return self.getData("projected_bill")

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = "total"
        attributes["budget_bill"] = self.getData("budget_bill")
        return attributes


# Defered Amount
class DeferedAmountSensor(FplMoneyEntity):
    """Defered amount sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Defered Amount")

    @property
    def state(self):
        if self.getData("budget_bill"):
            return self.getData("defered_amount")
        return 0

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = "total"
        return attributes


class ProjectedBudgetBillSensor(FplMoneyEntity):
    """projected budget bill sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Budget Bill")

    @property
    def state(self):
        return self.getData("budget_billing_projected_bill")

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = "total"
        return attributes


class ProjectedActualBillSensor(FplMoneyEntity):
    """projeted actual bill sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Actual Bill")

    @property
    def state(self):
        return self.getData("projected_bill")

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = "total"
        return attributes
