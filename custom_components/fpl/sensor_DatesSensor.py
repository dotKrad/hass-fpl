"""dates sensors"""
import datetime
from .fplEntity import FplDateEntity, FplDayEntity


class CurrentBillDateSensor(FplDateEntity):
    """Current bill date sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Current Bill Date")

    @property
    def native_value(self):
        return datetime.date.fromisoformat(self.getData("current_bill_date"))


class NextBillDateSensor(FplDateEntity):
    """Next bill date sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Next Bill Date")

    @property
    def native_value(self):
        return datetime.date.fromisoformat(self.getData("next_bill_date"))


class ServiceDaysSensor(FplDayEntity):
    """Service days sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Service Days")

    @property
    def native_value(self):
        return self.getData("service_days")


class AsOfDaysSensor(FplDayEntity):
    """As of days sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "As Of Days")

    @property
    def native_value(self):
        return self.getData("as_of_days")


class RemainingDaysSensor(FplDayEntity):
    """Remaining days sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Remaining Days")

    @property
    def native_value(self):
        return self.getData("remaining_days")
