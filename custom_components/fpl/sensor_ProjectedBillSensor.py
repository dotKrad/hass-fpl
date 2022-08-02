"""Projected bill sensors"""
from homeassistant.components.sensor import (
    # STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_TOTAL,
)
from .fplEntity import FplMoneyEntity


class FplProjectedBillSensor(FplMoneyEntity):
    """Projected bill sensor"""

    # _attr_state_class = STATE_CLASS_TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Bill")

    @property
    def native_value(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

        if budget and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_projected_bill")

        return self.getData("projected_bill")

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["budget_bill"] = self.getData("budget_bill")
        return attributes


# Defered Amount
class DeferedAmountSensor(FplMoneyEntity):
    """Defered amount sensor"""

    # _attr_state_class = STATE_CLASS_TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Defered Amount")

    @property
    def native_value(self):
        if self.getData("budget_bill"):
            return self.getData("defered_amount")
        return 0


class ProjectedBudgetBillSensor(FplMoneyEntity):
    """projected budget bill sensor"""

    # _attr_state_class = STATE_CLASS_TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Budget Bill")

    @property
    def native_value(self):
        return self.getData("budget_billing_projected_bill")


class ProjectedActualBillSensor(FplMoneyEntity):
    """projeted actual bill sensor"""

    # _attr_state_class = STATE_CLASS_TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Actual Bill")

    @property
    def native_value(self):
        return self.getData("projected_bill")
