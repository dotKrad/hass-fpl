"""energy sensors"""
from datetime import date, timedelta
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_TOTAL,
    DEVICE_CLASS_ENERGY,
)
from .fplEntity import FplEnergyEntity


class ProjectedKWHSensor(FplEnergyEntity):
    """Projected KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected KWH")

    @property
    def native_value(self):
        projectedKWH = self.getData("projectedKWH")

        if projectedKWH is not None:
            self._attr_native_value = projectedKWH

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes


class DailyAverageKWHSensor(FplEnergyEntity):
    """Daily Average KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average KWH")

    @property
    def native_value(self):
        dailyAverageKWH = self.getData("dailyAverageKWH")

        if dailyAverageKWH is not None:
            self._attr_native_value = dailyAverageKWH

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL
        return attributes


class BillToDateKWHSensor(FplEnergyEntity):
    """Bill To Date KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Bill To Date KWH")

    _attr_state_class = STATE_CLASS_TOTAL_INCREASING
    _attr_device_class = DEVICE_CLASS_ENERGY

    @property
    def native_value(self):
        billToDateKWH = self.getData("billToDateKWH")

        if billToDateKWH is not None:
            self._attr_native_value = billToDateKWH

        print(self.state_class)

        return self._attr_native_value


class NetReceivedKWHSensor(FplEnergyEntity):
    """Received Meter Reading KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Received Meter Reading KWH")

    @property
    def native_value(self):
        recMtrReading = self.getData("recMtrReading")

        if recMtrReading is not None:
            self._attr_native_value = recMtrReading

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL_INCREASING
        return attributes


class NetDeliveredKWHSensor(FplEnergyEntity):
    """Delivered Meter Reading KWH sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Delivered Meter Reading KWH")

    @property
    def native_value(self):
        delMtrReading = self.getData("delMtrReading")

        if delMtrReading is not None:
            self._attr_native_value = delMtrReading

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        # attributes["state_class"] = STATE_CLASS_TOTAL_INCREASING
        return attributes
