from .fplEntity import FplEntity


class FplDailyUsageSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage")

    @property
    def state(self):
        data = self.getData("daily_usage")

        if len(data) > 0:
            return data[-1]["cost"]

        return None

    def defineAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")

        if len(data) > 0:
            return {"date": data[-1]["date"]}

        return {}

    @property
    def icon(self):
        return "mdi:currency-usd"


class FplDailyUsageKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage KWH")

    @property
    def state(self):
        data = self.getData("daily_usage")

        if len(data) > 0:
            return data[-1]["usage"]

        return None

    def defineAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")

        if len(data) > 0:
            return {"date": data[-1]["date"]}

        return {}

    @property
    def icon(self):
        return "mdi:currency-usd"
