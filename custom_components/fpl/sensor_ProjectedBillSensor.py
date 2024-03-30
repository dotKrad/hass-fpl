"""Projected bill sensors"""
# from homeassistant.components.sensor import SensorStateClass.TOTAL

from .fplEntity import FplMoneyEntity


class FplProjectedBillSensor(FplMoneyEntity):
    """Projected bill sensor"""

    # _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Bill")

    @property
    def native_value(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

        projected_bill = self.getData("projected_bill")

        if budget and budget_billing_projected_bill is not None:
            self._attr_native_value = self.getData("budget_billing_projected_bill")
        else:
            if projected_bill is not None:
                self._attr_native_value = projected_bill

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["budget_bill"] = self.getData("budget_bill")
        return attributes


# Defered Amount
class DeferedAmountSensor(FplMoneyEntity):
    """Defered amount sensor"""

    # _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Defered Amount")

    @property
    def native_value(self):
        budget_bill = self.getData("budget_bill")
        defered_amount = self.getData("defered_amount")

        if budget_bill and defered_amount is not None:
            self._attr_native_value = defered_amount

        return self._attr_native_value


class ProjectedBudgetBillSensor(FplMoneyEntity):
    """projected budget bill sensor"""

    # _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Budget Bill")

    @property
    def native_value(self):
        budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

        if budget_billing_projected_bill is not None:
            self._attr_native_value = budget_billing_projected_bill

        return self._attr_native_value


class ProjectedActualBillSensor(FplMoneyEntity):
    """projeted actual bill sensor"""

    # _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Actual Bill")

    @property
    def native_value(self):
        projected_bill = self.getData("projected_bill")

        if projected_bill is not None:
            self._attr_native_value = projected_bill

        return self._attr_native_value


class BillToDateSensor(FplMoneyEntity):
    """projeted actual bill sensor"""

    # _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Bill To Date")

    @property
    def native_value(self):
        budget_bill = self.getData("budget_bill")
        budget_billing_bill_to_date = self.getData("budget_billing_bill_to_date")
        bill_to_date = self.getData("bill_to_date")

        if budget_bill:
            self._attr_native_value = budget_billing_bill_to_date
        else:
            self._attr_native_value = bill_to_date

        return self._attr_native_value
