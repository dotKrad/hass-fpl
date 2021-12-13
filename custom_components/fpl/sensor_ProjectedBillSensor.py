from .fplEntity import FplMoneyEntity


class FplProjectedBillSensor(FplMoneyEntity):
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


# Defered Amount
class DeferedAmountSensor(FplMoneyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Defered Amount")

    @property
    def state(self):
        if self.getData("budget_bill") == True:
            return self.getData("defered_amount")
        return 0


class ProjectedBudgetBillSensor(FplMoneyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Budget Bill")

    @property
    def state(self):
        return self.getData("budget_billing_projected_bill")


class ProjectedActualBillSensor(FplMoneyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Actual Bill")

    @property
    def state(self):
        return self.getData("projected_bill")
