from .fplEntity import FplEntity


class FplDailyUsageSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage")

    @property
    def state(self):
        data = self.getData("daily_usage")

        if (data is not None) and (len(data) > 0):
            return data[-1]["cost"]

        return None

    def defineAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")
        attributes = {}
        attributes["friendly_name"] = "Daily Usage"
        attributes["device_class"] = "monetary"
        attributes["state_class"] = "total_increasing"
        attributes["unit_of_measurement"] = "$"
        if data is not None:
            if (data[-1] is not None) and (data[-1]["readTime"] is not None):
                attributes["date"] = data[-1]["readTime"]
            if (data[-2] is not None) and (data[-2]["readTime"] is not None):
                attributes["last_reset"] = data[-2]["readTime"]
        return attributes

    @property
    def icon(self):
        return "mdi:currency-usd"


class FplDailyUsageKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage KWH")

    @property
    def state(self):
        data = self.getData("daily_usage")

        if (data is not None) and (data[-1]["usage"] is not None):
            return data[-1]["usage"]

        return None

    def defineAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")

        attributes = {}
        attributes["friendly_name"] = "Daily Usage"
        attributes["device_class"] = "energy"
        attributes["state_class"] = "total_increasing"
        attributes["unit_of_measurement"] = "kWh"

        if data is not None:
            if (data[-1] is not None) and (data[-1]["readTime"] is not None):
                attributes["date"] = data[-1]["readTime"]
            if (data[-2] is not None) and (data[-2]["readTime"] is not None):
                attributes["last_reset"] = data[-2]["readTime"]

        return attributes

    @property
    def icon(self):
        return "mdi:flash"


class FplDailyReceivedKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Received KWH")

    @property
    def state(self):
        data = self.getData("daily_usage")
        try:
            return data[-1]["netReceivedKwh"]
        except:
            return None

    def defineAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")

        attributes = {}
        attributes["friendly_name"] = "Daily Return to Grid"
        attributes["device_class"] = "energy"
        attributes["state_class"] = "total_increasing"
        attributes["unit_of_measurement"] = "kWh"
        if data is not None:
            if (data[-1] is not None) and (data[-1]["readTime"] is not None):
                attributes["date"] = data[-1]["readTime"]
            if (data[-2] is not None) and (data[-2]["readTime"] is not None):
                attributes["last_reset"] = data[-2]["readTime"]
        return attributes

    @property
    def icon(self):
        return "mdi:flash"


class FplDailyDeliveredKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Delivered KWH")

    @property
    def state(self):
        data = self.getData("daily_usage")
        try: 
            return data[-1]["netDeliveredKwh"]
        except:
            return None

    def defineAttributes(self):
        """Return the state attributes."""
        data = self.getData("daily_usage")

        attributes = {}
        attributes["friendly_name"] = "Daily Consumption"
        attributes["device_class"] = "energy"
        attributes["state_class"] = "total_increasing"
        attributes["unit_of_measurement"] = "kWh"
        if data is not None:
            if (data[-1] is not None) and (data[-1]["readTime"] is not None):
                attributes["date"] = data[-1]["readTime"]
            if (data[-2] is not None) and (data[-2]["readTime"] is not None):
                attributes["last_reset"] = data[-2]["readTime"]
        return attributes

    @property
    def icon(self):
        return "mdi:flash"
