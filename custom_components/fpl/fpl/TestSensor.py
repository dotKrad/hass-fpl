from .fplEntity import FplEntity
import pprint


class TestSensor(FplEntity):
    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Test Sensor")

    @property
    def state(self):
        pprint.pprint(self.coordinator.data)

        return self.getData("projected_bill")

    def defineAttributes(self):
        """Return the state attributes."""
        attributes = {}
        try:
            if self.getData("budget_bill"):
                attributes["budget_bill"] = self.getData("budget_bill")
        except:
            pass

        return attributes

    @property
    def icon(self):
        return "mdi:currency-usd"
