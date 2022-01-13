from .fplEntity import FplMoneyEntity


class FplAverageDailySensor(FplMoneyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average")

    @property
    def state(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_daily_avg")

        if budget == True and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_daily_avg")

        return self.getData("daily_avg")


class BudgetDailyAverageSensor(FplMoneyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Budget Daily Average")

    @property
    def state(self):
        return self.getData("budget_billing_daily_avg")


class ActualDailyAverageSensor(FplMoneyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Actual Daily Average")

    @property
    def state(self):
        return self.getData("daily_avg")
