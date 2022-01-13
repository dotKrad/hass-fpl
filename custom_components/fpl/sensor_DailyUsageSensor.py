from .fplEntity import FplEnergyEntity, FplMoneyEntity


class FplDailyUsageSensor(FplMoneyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage")

    @property
    def state(self):
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "cost" in data[-1].keys():
            return data[-1]["cost"]

        return None

    def defineAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "date" in data[-1].keys():
            return {"date": data[-1]["date"]}

        return {}


class FplDailyUsageKWHSensor(FplEnergyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage KWH")

    @property
    def state(self):
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "usage" in data[-1].keys():
            return data[-1]["usage"]

        return None

    def defineAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "date" in data[-1].keys():
            return {"date": data[-1]["date"]}

        return {}
