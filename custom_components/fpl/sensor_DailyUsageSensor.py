"""Daily Usage Sensors"""

from datetime import timedelta, datetime

# Updated imports:
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from .fplEntity import FplEnergyEntity, FplMoneyEntity


def _daily_usage_field(data, field):
    if not data:
        return None
    return data.get(field)


def _daily_usage_read_time(data):
    read_time = _daily_usage_field(data, "readTime")
    if read_time is None:
        return None
    return read_time - timedelta(days=1)


class FplDailyUsageSensor(FplMoneyEntity):
    """Daily Usage Cost Sensor (monetary)"""

    # If this sensor represents the cost *just for today* (not cumulative),
    # then use MEASUREMENT. If it's a cumulative total cost so far, use TOTAL_INCREASING.
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        billing_charge = _daily_usage_field(data, "billingCharge")
        if billing_charge is not None:
            self._attr_native_value = billing_charge
        return self._attr_native_value

    @property
    def last_reset(self) -> datetime | None:
        data = self.getData("DailyUsage")
        return _daily_usage_read_time(data)

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("DailyUsage")
        read_time = _daily_usage_field(data, "readTime")
        if read_time is None:
            return {}
        return {"date": read_time.strftime("%Y-%m-%d")}


class FplDailyUsageKWHSensor(FplEnergyEntity):
    """Daily Usage KWH Sensor"""

    # For daily usage, you might choose TOTAL if it's the total for that day
    # or TOTAL_INCREASING if you're incrementing throughout the day.
    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Usage KWH")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        kwh_actual = _daily_usage_field(data, "kwhActual")
        if kwh_actual is not None:
            self._attr_native_value = kwh_actual
        return self._attr_native_value

    @property
    def last_reset(self) -> datetime | None:
        """An optional last_reset property for daily totals."""
        data = self.getData("DailyUsage")
        return _daily_usage_read_time(data)

    def customAttributes(self):
        """Return any additional attributes."""
        data = self.getData("DailyUsage")
        read_time = _daily_usage_field(data, "readTime")
        if read_time is None:
            return {}
        return {"date": read_time.strftime("%Y-%m-%d")}


class FplDailyReceivedKWHSensor(FplEnergyEntity):
    """Daily Received KWH Sensor"""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Received KWH")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        kwh_actual = _daily_usage_field(data, "kwhActual")
        if kwh_actual is not None:
            self._attr_native_value = kwh_actual
        return self._attr_native_value

    @property
    def last_reset(self) -> datetime | None:
        data = self.getData("DailyUsage")
        return _daily_usage_read_time(data)

    def customAttributes(self):
        """Return any additional attributes."""
        data = self.getData("DailyUsage")
        read_time = _daily_usage_field(data, "readTime")
        if read_time is None:
            return {}
        return {"date": read_time.strftime("%Y-%m-%d")}


class FplDailyDeliveredKWHSensor(FplEnergyEntity):
    """Daily Delivered KWH Sensor"""

    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Delivered KWH")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        net_delivered_kwh = _daily_usage_field(data, "netDeliveredKwh")
        if net_delivered_kwh is not None:
            self._attr_native_value = net_delivered_kwh
        return self._attr_native_value

    @property
    def last_reset(self) -> datetime | None:
        data = self.getData("DailyUsage")
        return _daily_usage_read_time(data)

    def customAttributes(self):
        """Return any additional attributes."""
        data = self.getData("DailyUsage")
        read_time = _daily_usage_field(data, "readTime")
        if read_time is None:
            return {}
        return {"date": read_time.strftime("%Y-%m-%d")}


class FplDailyReceivedReading(FplEnergyEntity):
    """Daily Received Reading (Meter)"""

    # If this reading is continuously increasing, TOTAL_INCREASING is correct:
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Received Reading")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        reading = _daily_usage_field(data, "reading")
        if reading is not None:
            self._attr_native_value = reading
        return self._attr_native_value


class FplDailyDeliveredReading(FplEnergyEntity):
    """Daily Delivered Reading (Meter)"""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Delivered reading")

    @property
    def native_value(self):
        data = self.getData("DailyUsage")
        net_delivered_reading = _daily_usage_field(data, "netDeliveredReading")
        if net_delivered_reading is not None:
            self._attr_native_value = net_delivered_reading
        return self._attr_native_value
