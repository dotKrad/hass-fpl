"""energy sensors"""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from .fplEntity import FplEnergyEntity


class ProjectedKWHSensor(FplEnergyEntity):
    """Projected KWH sensor"""

    # Typically, a "projected" value is not strictly cumulative.
    # Use MEASUREMENT or TOTAL (without _INCREASING) as needed.
    # For now, let's assume it's a measurement of an estimation.
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected KWH")

    @property
    def native_value(self):
        projectedKWH = self.getData("projectedKWH")

        if projectedKWH is not None:
            self._attr_native_value = projectedKWH

        return self._attr_native_value


class DailyAverageKWHSensor(FplEnergyEntity):
    """Daily Average KWH sensor"""

    # Averages are often treated as measurements too, not cumulative totals.
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average KWH")

    @property
    def native_value(self):
        dailyAverageKWH = self.getData("dailyAverageKWH")

        if dailyAverageKWH is not None:
            self._attr_native_value = dailyAverageKWH

        return self._attr_native_value


class BillToDateKWHSensor(FplEnergyEntity):
    """Bill To Date KWH sensor"""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Bill To Date KWH")

    @property
    def native_value(self):
        billToDateKWH = self.getData("billToDateKWH")

        if billToDateKWH is not None:
            self._attr_native_value = billToDateKWH

        return self._attr_native_value


class NetReceivedKWHSensor(FplEnergyEntity):
    """Received Meter Reading KWH sensor"""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Received Meter Reading KWH")

    @property
    def native_value(self):
        recMtrReading = self.getData("recMtrReading")

        if recMtrReading is not None:
            self._attr_native_value = recMtrReading

        return self._attr_native_value


class NetDeliveredKWHSensor(FplEnergyEntity):
    """Delivered Meter Reading KWH sensor"""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Delivered Meter Reading KWH")

    @property
    def native_value(self):
        delMtrReading = self.getData("delMtrReading")

        if delMtrReading is not None:
            self._attr_native_value = delMtrReading

        return self._attr_native_value
