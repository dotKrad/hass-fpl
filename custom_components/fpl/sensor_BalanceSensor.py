"""Balance sensors"""
from .fplEntity import FplMoneyEntity


class BalanceSensor(FplMoneyEntity):
    """balance sensor"""

    def __init__(self, coordinator, config, account):
        super().__init__(coordinator, config, account, "Balance Due")

    @property
    def native_value(self):
        data = self.getData("balance_data")

        self._attr_native_value = 0

        if data is not None and len(data) > 0 and "amount" in data[0].keys():
            self._attr_native_value = data[0]["amount"]

        return self._attr_native_value

    def customAttributes(self):
        """Return the state attributes."""
        attributes = {}
        data = self.getData("balance_data")

        if data is not None and len(data) > 0:
            if "details" in data[0].keys():
                attributes["details"] = data[0]["details"]
            if "dueDate" in data[0].keys():
                attributes["dueDate"] = data[0]["dueDate"]

        return attributes
