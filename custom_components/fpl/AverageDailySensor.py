from .FplSensor import FplSensor


class FplAverageDailySensor(FplSensor):
    def __init__(self, hass, config, account):
        FplSensor.__init__(self, hass, config, account, "Average Daily")

    @property
    def state(self):
        return self.data["daily_avg"]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr