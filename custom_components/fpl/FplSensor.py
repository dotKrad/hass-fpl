from homeassistant.helpers.entity import Entity
from homeassistant import util
from .const import DOMAIN, DOMAIN_DATA, ATTRIBUTION
from datetime import timedelta

MIN_TIME_BETWEEN_SCANS = timedelta(minutes=30)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)


class FplSensor(Entity):
    def __init__(self, hass, config, account, sensorName):
        self._config = config
        self._state = None
        self.loop = hass.loop

        self._account = account
        self.attr = {}
        self.data = None
        self.sensorName = sensorName

    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Update the sensor."""
        # Send update "signal" to the component
        # await self.hass.data[DOMAIN_DATA]["client"].update_data()

        # Get new data (if any)
        if "data" in self.hass.data[DOMAIN_DATA]:
            self.data = self.hass.data[DOMAIN_DATA]["data"][self._account]

            # Set/update attributes
            self.attr["attribution"] = ATTRIBUTION

    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._account)},
            "name": f"Account {self._account}",
            "manufacturer": "Florida Power & Light",
        }

    @property
    def unique_id(self):
        """Return the ID of this device."""
        id = "{}{}{}".format(
            DOMAIN, self._account, self.sensorName.lower().replace(" ", "")
        )
        return id

    @property
    def name(self):
        return f"{DOMAIN.upper()} {self._account} {self.sensorName}"

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return "mdi:flash"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr