from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING
from .fplEntity import FplEnergyEntity


class ProjectedKWHSensor(FplEnergyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected KWH")

    @property
    def state(self):
        return self.getData("projectedKWH")


class DailyAverageKWHSensor(FplEnergyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average KWH")

    @property
    def state(self):
        return self.getData("dailyAverageKWH")


class BillToDateKWHSensor(FplEnergyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Bill To Date KWH")

    @property
    def state(self):
        return self.getData("billToDateKWH")

    @property
    def state_class(self) -> str:
        """Return the state class of this entity, from STATE_CLASSES, if any."""


class NetReceivedKWHSensor(FplEnergyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Received Meter Reading KWH")

    @property
    def state(self):
        return self.getData("recMtrReading")

    @property
    def icon(self):
        return "mdi:flash"


class NetDeliveredKWHSensor(FplEnergyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Delivered Meter Reading KWH")

    @property
    def state(self):
        return self.getData("delMtrReading")

    @property
    def icon(self):
        return "mdi:flash"
