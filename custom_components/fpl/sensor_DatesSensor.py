from .fplEntity import FplEntity


class CurrentBillDateSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Current Bill Date")

    @property
    def state(self):
        return self.getData("current_bill_date")

    @property
    def icon(self):
        return "mdi:calendar"


class NextBillDateSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Next Bill Date")

    @property
    def state(self):
        return self.getData("next_bill_date")

    @property
    def icon(self):
        return "mdi:calendar"


class ServiceDaysSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Service Days")

    @property
    def state(self):
        return self.getData("service_days")

    @property
    def icon(self):
        return "mdi:calendar"


class AsOfDaysSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "As Of Days")

    @property
    def state(self):
        return self.getData("as_of_days")

    @property
    def icon(self):
        return "mdi:calendar"


class RemainingDaysSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Remaining Days")

    @property
    def state(self):
        return self.getData("remaining_days")

    @property
    def icon(self):
        return "mdi:calendar"
