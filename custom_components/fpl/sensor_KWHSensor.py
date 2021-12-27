from .fplEntity import FplEntity


class ProjectedKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected KWH")

    @property
    def state(self):
        return self.getData("projectedKWH")

    @property
    def icon(self):
        return "mdi:flash"


class DailyAverageKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average KWH")

    @property
    def state(self):
        return self.getData("dailyAverageKWH")

    @property
    def icon(self):
        return "mdi:flash"


class BillToDateKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Bill To Date KWH")

    @property
    def state(self):
        return self.getData("billToDateKWH")

    @property
    def icon(self):
        return "mdi:flash"

class NetReceivedKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Received Meter Reading KWH")

    @property
    def state(self):
        return self.getData("recMtrReading")

    @property
    def icon(self):
        return "mdi:flash"

class NetDeliveredKWHSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Delivered Meter Reading KWH")

    @property
    def state(self):
        return self.getData("delMtrReading")

    @property
    def icon(self):
        return "mdi:flash"
