from .FplSensor import FplSensor


class FplAverageDailySensor(FplSensor):
    def __init__(self, hass, config, account):
        FplSensor.__init__(self, hass, config, account, "Average Daily")

    @property
    def state(self):
        try:
            if "daily_avg" in self.data:
                self._state = self.data["daily_avg"]
        except:
            pass
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr