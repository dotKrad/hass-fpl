"""Average daily sensors"""
from homeassistant.components.sensor import STATE_CLASS_TOTAL
from .fplEntity import FplMoneyEntity


class DailyAverageSensor(FplMoneyEntity):
    """average daily sensor, use budget value if available, otherwise use actual daily values"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average")

    @property
    def state(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_daily_avg")

        if budget and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_daily_avg")

        try:
            self._state=self.getData("daily_avg")
        except:
            pass
        return self._state

<<<<<<< HEAD
=======
    @property
    def icon(self):
        return "mdi:currency-usd"

<<<<<<< HEAD:custom_components/fpl1/sensor_AverageDailySensor.py
    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes

=======
    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Daily Average"
        attributes["device_class"] = "monetary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes
>>>>>>> master
>>>>>>> master:custom_components/fpl/sensor_AverageDailySensor.py

class BudgetDailyAverageSensor(FplMoneyEntity):
    """budget daily average sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Budget Daily Average")

    @property
    def state(self):
        try:
            self._state= self.getData("budget_billing_daily_avg")
        except:
            pass
        return self._state

<<<<<<< HEAD:custom_components/fpl1/sensor_AverageDailySensor.py
    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes

=======
<<<<<<< HEAD
>>>>>>> master:custom_components/fpl/sensor_AverageDailySensor.py

class ActualDailyAverageSensor(FplMoneyEntity):
    """Actual daily average sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Actual Daily Average")

    @property
    def state(self):
        return self.getData("daily_avg")
<<<<<<< HEAD:custom_components/fpl1/sensor_AverageDailySensor.py

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes
=======
=======
    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Budget Daily Average"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes

>>>>>>> master
>>>>>>> master:custom_components/fpl/sensor_AverageDailySensor.py
