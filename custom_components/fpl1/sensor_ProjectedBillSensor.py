"""Projected bill sensors"""
from homeassistant.components.sensor import (
    # STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_TOTAL,
)
from .fplEntity import FplMoneyEntity


class FplProjectedBillSensor(FplMoneyEntity):
    """projected bill sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Bill")

    @property
    def native_value(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

        if budget and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_projected_bill")

        return self.getData("projected_bill")

    """
    @property
    def state(self):
        budget = self.getData("budget_bill")
        budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

<<<<<<< HEAD:custom_components/fpl1/sensor_ProjectedBillSensor.py
        if budget and budget_billing_projected_bill is not None:
            return self.getData("budget_billing_projected_bill")

        return self.getData("projected_bill")
    """
=======
        try:
            if budget == True and budget_billing_projected_bill is not None:
                self._state = self.getData("budget_billing_projected_bill")
            else:
                self._state = self.getData("projected_bill")
        except:
            self._state = None
        return self._state
>>>>>>> master:custom_components/fpl/sensor_ProjectedBillSensor.py

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
<<<<<<< HEAD:custom_components/fpl1/sensor_ProjectedBillSensor.py
        attributes["state_class"] = STATE_CLASS_TOTAL
        attributes["budget_bill"] = self.getData("budget_bill")
=======
        attributes["friendly_name"] = "Projected Bill Payment Due"
        attributes["device_class"] = "monetary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
>>>>>>> master:custom_components/fpl/sensor_ProjectedBillSensor.py
        return attributes


# Defered Amount
class DeferedAmountSensor(FplMoneyEntity):
    """Defered amount sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Deferred Amount")

    @property
    def state(self):
<<<<<<< HEAD:custom_components/fpl1/sensor_ProjectedBillSensor.py
        if self.getData("budget_bill"):
            return self.getData("defered_amount")
        return 0

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes

=======
        try:
            self._state = self.getData("deferred_amount")
        except:
            self._state = 0
            pass
        return self._state

<<<<<<< HEAD
=======
    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Deferred Amount"
        attributes["device_class"] = "monetary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes

>>>>>>> master
>>>>>>> master:custom_components/fpl/sensor_ProjectedBillSensor.py

class ProjectedBudgetBillSensor(FplMoneyEntity):
    """projected budget bill sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Budget Bill")

    @property
    def state(self):
        try:
            self._state = self.getData("budget_billing_projected_bill")
        except:
            pass
        return self._state

<<<<<<< HEAD
=======
    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Projected Budget Bill"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"
        return attributes

<<<<<<< HEAD:custom_components/fpl1/sensor_ProjectedBillSensor.py
    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes

=======
>>>>>>> master
>>>>>>> master:custom_components/fpl/sensor_ProjectedBillSensor.py

class ProjectedActualBillSensor(FplMoneyEntity):
    """projeted actual bill sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected Actual Bill")

    @property
    def state(self):
<<<<<<< HEAD
        return self.getData("projected_bill")
<<<<<<< HEAD:custom_components/fpl1/sensor_ProjectedBillSensor.py

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes
=======
=======
        try:
            self._state = self.getData("projected_bill")
        except:
            pass
        return self._state

    @property
    def icon(self):
        return "mdi:currency-usd"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Projected Actual Bill"
        attributes["device_class"] = "monitary"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "$"

        return attributes
>>>>>>> master
>>>>>>> master:custom_components/fpl/sensor_ProjectedBillSensor.py
