"""dates sensors"""
import datetime
from .fplEntity import FplDateEntity, FplDayEntity


class CurrentBillDateSensor(FplDateEntity):
    """Current bill date sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Current Bill Date")

    @property
    def native_value(self):
        current_bill_date = self.getData("current_bill_date")

        if current_bill_date is not None:
            self._attr_native_value = datetime.date.fromisoformat(current_bill_date)

        return self._attr_native_value


class NextBillDateSensor(FplDateEntity):
    """Next bill date sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Next Bill Date")

    @property
    def native_value(self):
        next_bill_date = self.getData("next_bill_date")

        if next_bill_date is not None:
            self._attr_native_value = datetime.date.fromisoformat(next_bill_date)

        return self._attr_native_value


class ServiceDaysSensor(FplDayEntity):
    """Service days sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Service Days")

    @property
    def native_value(self):
        service_days = self.getData("service_days")

        if service_days is not None:
            self._attr_native_value = service_days

        return self._attr_native_value


class AsOfDaysSensor(FplDayEntity):
    """As of days sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "As Of Days")

    @property
    def native_value(self):
        as_of_days = self.getData("as_of_days")

        if as_of_days is not None:
            self._attr_native_value = as_of_days

        return self._attr_native_value


class RemainingDaysSensor(FplDayEntity):
    """Remaining days sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Remaining Days")

    @property
    def native_value(self):
        remaining_days = self.getData("remaining_days")

        if remaining_days is not None:
            self._attr_native_value = remaining_days

        return self._attr_native_value
