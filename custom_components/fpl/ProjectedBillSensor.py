from .FplSensor import FplSensor


class FplProjectedBillSensor(FplSensor):
    def __init__(self, hass, config, account):
        FplSensor.__init__(self, hass, config, account, "Projected Bill")

    @property
    def state(self):
        data = self.data
        if "budget_bill" in data.keys():
            if data["budget_bill"]:
                if "budget_billing_projected_bill" in data.keys():
                    self._state = data["budget_billing_projected_bill"]
            else:
                if "projected_bill" in data.keys():
                    self._state = data["projected_bill"]

        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if "budget_bill" in self.data.keys():
            self.attr["budget_bill"] = self.data["budget_bill"]
        return self.attr

    @property
    def icon(self):
        return "mdi:currency-usd"