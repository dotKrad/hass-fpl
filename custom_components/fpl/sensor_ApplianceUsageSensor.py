"""Average daily sensors"""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from .fplEntity import FplMoneyEntity, FplEnergyEntity

from datetime import datetime


class ApplianceCostSensor(FplMoneyEntity):
    """Appliance Cost Sensor"""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    CATEGORY_NAME = None
    NAME = None

    def __init__(self, coordinator, config, account):
        assert self.CATEGORY_NAME is not None, "CATEGORY_NAME must be set"
        if self.NAME is None:
            self.NAME = self.CATEGORY_NAME
        super().__init__(coordinator, config, account, f"{self.NAME.title()} Cost")

    @property
    def native_value(self):
        appliance_usage = self.getData("appliance_usage")
        if not appliance_usage:
            return self._attr_native_value
        categories = appliance_usage.get("categories") or []
        for category in categories:
            if category.get("category").lower() == self.CATEGORY_NAME.lower():
                self._attr_native_value = category.get("cost")
                return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        appliance_usage = self.getData("appliance_usage")
        if not appliance_usage:
            return {}
        start_date = appliance_usage.get("startDate")
        end_date = appliance_usage.get("endDate")
        if not start_date or not end_date:
            return {}
        return {
            "startDate": datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d"),
            "endDate": datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d"),
        }


class ApplianceUsageSensor(FplEnergyEntity):
    """Appliance Usage Sensor in KWH"""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    CATEGORY_NAME = None
    NAME = None

    def __init__(self, coordinator, config, account):
        assert self.CATEGORY_NAME is not None, "CATEGORY_NAME must be set"
        if self.NAME is None:
            self.NAME = self.CATEGORY_NAME
        super().__init__(coordinator, config, account, f"{self.NAME.title()} Usage kWh")

    @property
    def native_value(self):
        appliance_usage = self.getData("appliance_usage")
        if not appliance_usage:
            return self._attr_native_value
        categories = appliance_usage.get("categories") or []
        for category in categories:
            if category.get("category").lower() == self.CATEGORY_NAME.lower():
                self._attr_native_value = category.get("kwh")
                return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        appliance_usage = self.getData("appliance_usage")
        if not appliance_usage:
            return {}
        start_date = appliance_usage.get("startDate")
        end_date = appliance_usage.get("endDate")
        if not start_date or not end_date:
            return {}
        return {
            "startDate": datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d"),
            "endDate": datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d"),
        }


class CoolingCostSensor(ApplianceCostSensor):
    """Cooling Cost Sensor"""

    CATEGORY_NAME = "Cooling"


class CoolingUsageSensor(ApplianceUsageSensor):
    """Cooling Usage Sensor in KWH"""

    CATEGORY_NAME = "Cooling"


class WaterHeaterCostSensor(ApplianceCostSensor):
    """Water Heater Cost Sensor"""

    CATEGORY_NAME = "waterHeater"
    NAME = "Water Heater"


class WaterHeaterUsageSensor(ApplianceUsageSensor):
    """Heating Usage Sensor in KWH"""

    CATEGORY_NAME = "waterHeater"
    NAME = "Water Heater"


class LaundryCostSensor(ApplianceCostSensor):
    """Laundry Cost Sensor"""

    CATEGORY_NAME = "laundry"


class LaundryUsageSensor(ApplianceUsageSensor):
    """Laundry Usage Sensor in KWH"""

    CATEGORY_NAME = "laundry"


class RefrigerationCostSensor(ApplianceCostSensor):
    """Refrigeration Cost Sensor"""

    CATEGORY_NAME = "refrigeration"


class RefrigerationUsageSensor(ApplianceUsageSensor):
    """Refrigeration Usage Sensor in KWH"""

    CATEGORY_NAME = "refrigeration"


class PoolCostSensor(ApplianceCostSensor):
    """Pool Cost Sensor"""

    CATEGORY_NAME = "pool"


class PoolUsageSensor(ApplianceUsageSensor):
    """Pool Usage Sensor in KWH"""

    CATEGORY_NAME = "pool"


class LightingCostSensor(ApplianceCostSensor):
    """Lighting Cost Sensor"""

    CATEGORY_NAME = "lighting"


class LightingUsageSensor(ApplianceUsageSensor):
    """Lighting Usage Sensor in KWH"""

    CATEGORY_NAME = "lighting"


class EntertainmentCostSensor(ApplianceCostSensor):
    """Entertainment Cost Sensor"""

    CATEGORY_NAME = "entertainment"


class EntertainmentUsageSensor(ApplianceUsageSensor):
    """Entertainment Usage Sensor in KWH"""

    CATEGORY_NAME = "entertainment"


class CookingCostSensor(ApplianceCostSensor):
    """Cooking Cost Sensor"""

    CATEGORY_NAME = "cooking"


class CookingUsageSensor(ApplianceUsageSensor):
    """Cooking Usage Sensor in KWH"""

    CATEGORY_NAME = "cooking"


class MiscellaneousCostSensor(ApplianceCostSensor):
    """Miscellaneous Cost Sensor"""

    CATEGORY_NAME = "misc"
    NAME = "Miscellaneous"


class MiscellaneousUsageSensor(ApplianceUsageSensor):
    """Miscellaneous Usage Sensor in KWH"""

    CATEGORY_NAME = "misc"
    NAME = "Miscellaneous"
