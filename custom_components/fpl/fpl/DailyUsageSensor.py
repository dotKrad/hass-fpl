from .FplSensor import FplSensor


class FplDailyUsageSensor(FplSensor):
    def __init__(self, hass, config, account):
        FplSensor.__init__(self, hass, config, account, "Daily Usage")

    @property
    def state(self):
        try:
            if "daily_usage" in self.data:
                if len(self.data["daily_usage"]) > 0:
                    if "cost" in self.data["daily_usage"][-1]:
                        self._state = self.data["daily_usage"][-1]["cost"]
        except:
            pass

        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        try:
            if "daily_usage" in self.data:
                if len(self.data["daily_usage"]) > 0:
                    if "date" in self.data["daily_usage"][-1]:
                        self.attr["date"] = self.data["daily_usage"][-1]["date"]
        except:
            pass

        return self.attr
