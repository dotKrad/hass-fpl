<<<<<<< HEAD:custom_components/fpl1/sensor_DatesSensor.py
"""dates sensors"""
import datetime
from .fplEntity import FplDateEntity, FplDayEntity
=======
<<<<<<< HEAD
from .fplEntity import FplDateEntity
>>>>>>> master:custom_components/fpl/sensor_DatesSensor.py

=======
from .fplEntity import FplEntity
import datetime
>>>>>>> master

class CurrentBillDateSensor(FplDateEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing Current Date")

    @property
    def state(self):
<<<<<<< HEAD:custom_components/fpl1/sensor_DatesSensor.py
        return datetime.date.fromisoformat(self.getData("current_bill_date"))
=======
        try:
            self._state= datetime.date.fromisoformat(self.getData("current_bill_date"))
        except:
            pass
        return self._state
>>>>>>> master:custom_components/fpl/sensor_DatesSensor.py

<<<<<<< HEAD
=======
    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["device_class"] = "date"
        attributes["friendly_name"] = "Billing Current"
        return attributes
>>>>>>> master

class NextBillDateSensor(FplDateEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing Next")

    @property
    def state(self):
<<<<<<< HEAD:custom_components/fpl1/sensor_DatesSensor.py
        return datetime.date.fromisoformat(self.getData("next_bill_date"))


class ServiceDaysSensor(FplDayEntity):
=======
        try:
            self._state= datetime.date.fromisoformat(self.getData("next_bill_date"))
        except:
            pass
        return self._state


<<<<<<< HEAD
class ServiceDaysSensor(FplDateEntity):
=======
    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["device_class"] = "date"
        attributes["friendly_name"] = "Billing Next"
        return attributes

class ServiceDaysSensor(FplEntity):
>>>>>>> master
>>>>>>> master:custom_components/fpl/sensor_DatesSensor.py
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing Total Days")

    @property
    def state(self):
        try:
            self._state= self.getData("service_days")
        except:
            pass
        return self._state

<<<<<<< HEAD
=======
    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["unit_of_measurement"] = "days"
        attributes["friendly_name"] = "Billing Total"
        return attributes
>>>>>>> master

class AsOfDaysSensor(FplDayEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing As Of")

    @property
    def state(self):
        try:
            self._state= self.getData("as_of_days")
        except:
            pass
        return self._state

<<<<<<< HEAD
=======
    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["unit_of_measurement"] = "days"
        attributes["friendly_name"] = "Billing As Of"
        return attributes
>>>>>>> master

class RemainingDaysSensor(FplDayEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Billing Remaining")

    @property
    def state(self):
<<<<<<< HEAD
        return self.getData("remaining_days")
=======
        try:
            self._state= self.getData("remaining_days")
        except:
            pass
        return self._state

    @property
    def icon(self):
        return "mdi:calendar"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["unit_of_measurement"] = "days"
        attributes["friendly_name"] = "Billing Remaining"
        return attributes
>>>>>>> master
