from .fplEntity import FplDateEntity


class CurrentBillDateSensor(FplDateEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Current Bill Date")

    @property
    def state(self):
        return self.getData("current_bill_date")


class NextBillDateSensor(FplDateEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Next Bill Date")

    @property
    def state(self):
        return self.getData("next_bill_date")


class ServiceDaysSensor(FplDateEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Service Days")

    @property
    def state(self):
        return self.getData("service_days")


class AsOfDaysSensor(FplDateEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "As Of Days")

    @property
    def state(self):
        return self.getData("as_of_days")


class RemainingDaysSensor(FplDateEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Remaining Days")

    @property
    def state(self):
        return self.getData("remaining_days")
