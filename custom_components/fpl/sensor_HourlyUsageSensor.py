"""Hourly Usage Sensors"""
from datetime import timedelta, datetime
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_TOTAL,
    DEVICE_CLASS_ENERGY,
)
from .fplEntity import FplEnergyEntity, FplMoneyEntity
#from homeassistant_historical_sensor import (
#    HistoricalSensor, HistoricalState, PollUpdateMixin,
#)


class FplHourlyUsageSensor(FplMoneyEntity):
    """Hourly Usage Cost Sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Hourly Usage")

    @property
    def native_value(self):
        data = self.getData("hourly_usage")

        if data is not None and len(data) > 0 and "cost" in data[-1].keys():
            self._attr_native_value = data[-1]["cost"]

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        data = self.getData("hourly_usage")
        attributes = {}

        if data is not None and len(data) > 0 and "readTime" in data[-1].keys():
            attributes["date"] = data[-1]["readTime"]

        return attributes


class FplHourlyUsageKWHSensor(FplEnergyEntity):
    """Hourly Usage Kwh Sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Hourly Usage KWH")

    # _attr_state_class = STATE_CLASS_TOTAL
    _attr_device_class = DEVICE_CLASS_ENERGY

    @property def statistic_id(self) -> str:
        return self.entity_id
        
    #@property
    #def native_value(self):
    #    data = self.getData("hourly_usage")

    #    if data is not None and len(data) > 0 and "kwhActual" in data[-1].keys():
    #        self._attr_native_value = data[-1]["kwhActual"]

    #    return self._attr_native_value

    #@property
    #def last_reset(self) -> datetime | None:
    #    data = self.getData("hourly_usage")
    #    if data is not None and len(data) > 0 and "readTime" in data[-1].keys():
    #        date = data[-1]["readTime"]
    #        _attr_last_reset = date
    #    else:
    #        _attr_last_reset = None

    #    return _attr_last_reset

    def customAttributes(self):
 
        attributes = {}
 
        return attributes


class FplHourlyReceivedKWHSensor(FplEnergyEntity):
    """hourly received Kwh sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Hourly Received KWH")

    def get_statistic_metadata(self) -> StatisticMetaData:
        meta = super().get_statistic_metadata() meta["has_sum"] = True
        meta["has_mean"] = True

        return meta
        
    # _attr_state_class = STATE_CLASS_TOTAL
    _attr_device_class = DEVICE_CLASS_ENERGY
    
    @property def statistic_id(self) -> str:
        return self.entity_id
        

    #@property
    #def native_value(self):
    #    data = self.getData("hourly_usage")

    #    if data is not None and len(data) > 0 and "netReceived" in data[-1].keys():
    #        self._attr_native_value = data[-1]["netReceived"]

    #    return self._attr_native_value

    #@property
    #def last_reset(self) -> datetime | None:
    #    data = self.getData("hourly_usage")
    #    if data is not None and len(data) > 0 and "readTime" in data[-1].keys():
    #        date = data[-1]["readTime"]
    #        _attr_last_reset = date
    #    else:
    #        _attr_last_reset = None

    #    return _attr_last_reset
        
    def customAttributes(self):
  
        attributes = {}

        return attributes


class FplHourlyDeliveredKWHSensor(FplEnergyEntity):
    """hourly delivered Kwh sensor"""

    #_attr_state_class = STATE_CLASS_TOTAL
    _attr_device_class = DEVICE_CLASS_ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Hourly Delivered KWH")

    #@property
    #def native_value(self):
    #    data = self.getData("hourly_usage")

    #    if data is not None and len(data) > 0 and "netDelivered" in data[-1].keys():
    #        self._attr_native_value = data[-1]["netDelivered"]

    #    return self._attr_native_value

    #@property
    #def last_reset(self) -> datetime | None:
    #    data = self.getData("hourly_usage")
    #    if data is not None and len(data) > 0 and "readTime" in data[-1].keys():
    #        date = data[-1]["readTime"]
    #        _attr_last_reset = date
    #    else:
    #        _attr_last_reset = None

    #    return _attr_last_reset
        
    def customAttributes(self):

        attributes = {}

        return attributes

class FplHourlyReadingKWHSensor(FplEnergyEntity):
    """hourly reading Kwh sensor"""

    #_attr_state_class = STATE_CLASS_TOTAL_INCREASING
    _attr_device_class = DEVICE_CLASS_ENERGY

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Hourly reading KWH")

    #@property
    #def native_value(self):
    #    data = self.getData("hourly_usage")

    #    if data is not None and len(data) > 0 and "reading" in data[-1].keys():
    #        self._attr_native_value = data[-1]["reading"]

    #    return self._attr_native_value

 
    def customAttributes(self):

        attributes = {}

        return attributes