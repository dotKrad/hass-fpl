from .fplEntity import FplEntity
import datetime

class CurrentBillDateSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing Current Date")

    @property
    def state(self):
        return datetime.date.fromisoformat(self.getData("current_bill_date"))

    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["device_class"] = "date"
        attributes["friendly_name"] = "Billing Current"
        return attributes

class NextBillDateSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing Next")

    @property
    def state(self):
        return datetime.date.fromisoformat(self.getData("next_bill_date"))

    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["device_class"] = "date"
        attributes["friendly_name"] = "Billing Next"
        return attributes

class ServiceDaysSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing Total Days")

    @property
    def state(self):
        return self.getData("service_days")

    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["unit_of_measurement"] = "days"
        attributes["friendly_name"] = "Billing Total"
        return attributes

class AsOfDaysSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing As Of")

    @property
    def state(self):
        return self.getData("as_of_days")

    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["unit_of_measurement"] = "days"
        attributes["friendly_name"] = "Billing As Of"
        return attributes

class RemainingDaysSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing Remaining")

    @property
    def state(self):
        return self.getData("remaining_days")

    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["unit_of_measurement"] = "days"
        attributes["friendly_name"] = "Billing Remaining"
        return attributes
