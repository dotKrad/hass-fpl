from .FplSensor import FplSensor


class FplDailyUsageSensor(FplSensor):
    def __init__(self, hass, config, account):
        FplSensor.__init__(self, hass, config, account, "Daily Usage")

    @property
    def state(self):
        return self.data["daily_usage"][-1]["cost"]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        self.attr["date"] = self.data["daily_usage"][-1]["date"]
        return self.attr
