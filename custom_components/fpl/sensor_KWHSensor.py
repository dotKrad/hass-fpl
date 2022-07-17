from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING
from .fplEntity import FplEnergyEntity


class ProjectedKWHSensor(FplEnergyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Projected")

    @property
    def state(self):
        try:
            self._state = self.getData("projectedKWH")
        except:
            pass
        return self._state


<<<<<<< HEAD
class DailyAverageKWHSensor(FplEnergyEntity):
=======
    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Projected KWH"
        attributes["device_class"] = "energy"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "kWh"
        return attributes


class DailyAverageKWHSensor(FplEntity):
>>>>>>> master
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Daily Average KWH")

    @property
    def state(self):
        try:
            self._state = self.getData("dailyAverageKWH")
        except:
            pass
        return self._state

<<<<<<< HEAD
=======
    @property
    def icon(self):
        return "mdi:flash"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Daily Average"
        attributes["device_class"] = "energy"
        attributes["state_class"] = "total"
        attributes["unit_of_measurement"] = "kWh"
        return attributes

>>>>>>> master

class BillToDateKWHSensor(FplEnergyEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Bill To Date")

    @property
    def state(self):
        try:
            self._state = self.getData("billToDateKWH")
        except:
            pass
        return self._state

    @property
    def state_class(self) -> str:
        """Return the state class of this entity, from STATE_CLASSES, if any."""


<<<<<<< HEAD
class NetReceivedKWHSensor(FplEnergyEntity):
=======
    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Billing Usage"
        attributes["device_class"] = "energy"
        attributes["state_class"] = "total_increasing"
        attributes["unit_of_measurement"] = "kWh"
        if self.getData("billStartDate") is not None:
            attributes["last_reset"] = self.getData("billStartDate")
        return attributes


class NetReceivedKWHSensor(FplEntity):
>>>>>>> master
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Received Reading")

    @property
    def state(self):
        try:
            self._state = self.getData("recMtrReading")
        except:
            pass
        return self._state

    @property
    def icon(self):
        return "mdi:flash"

<<<<<<< HEAD

class NetDeliveredKWHSensor(FplEnergyEntity):
=======
    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Meter Return to Grid"
        attributes["device_class"] = "energy"
        attributes["state_class"] = "total_increasing"
        attributes["unit_of_measurement"] = "kWh"
        if self.getData("billStartDate") is not None:
            attributes["last_reset"] = self.getData("billStartDate")

        return attributes


class NetDeliveredKWHSensor(FplEntity):
>>>>>>> master
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Delivered Reading")

    @property
    def state(self):
        try:
            self._state = self.getData("delMtrReading")
        except:
            try:
                self._state = self.getData("billToDateKWH")
            except:
                pass
        return self._state

    @property
    def icon(self):
        return "mdi:flash"

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        attributes["friendly_name"] = "Meter Consumption"
        attributes["device_class"] = "energy"
        attributes["state_class"] = "total_increasing"
        attributes["unit_of_measurement"] = "kWh"
        if self.getData("billStartDate") is not None:
            attributes["last_reset"] = self.getData("billStartDate")

        return attributes
