"""Sensor platform for integration_blueprint."""

from .sensor_KWHSensor import (
    ProjectedKWHSensor,
    DailyAverageKWHSensor,
    BillToDateKWHSensor,
)
from .sensor_DatesSensor import (
    CurrentBillDateSensor,
    NextBillDateSensor,
    ServiceDaysSensor,
    AsOfDaysSensor,
    RemainingDaysSensor,
)
from .sensor_ProjectedBillSensor import (
    FplProjectedBillSensor,
    ProjectedBudgetBillSensor,
    ProjectedActualBillSensor,
    DeferedAmountSensor,
)
from .sensor_AverageDailySensor import (
    FplAverageDailySensor,
    BudgetDailyAverageSensor,
    ActualDailyAverageSensor,
)
from .sensor_DailyUsageSensor import FplDailyUsageSensor
from .const import DOMAIN

from .sensor_AllData import AllDataSensor
from .TestSensor import TestSensor


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    accounts = entry.data.get("accounts")

    coordinator = hass.data[DOMAIN][entry.entry_id]
    fpl_accounts = []

    for account in accounts:
        # Test Sensor
        # fpl_accounts.append(TestSensor(coordinator, entry, account))
        # All data sensor
        # fpl_accounts.append(AllDataSensor(coordinator, entry, account))

        # bill sensors
        fpl_accounts.append(FplProjectedBillSensor(coordinator, entry, account))
        fpl_accounts.append(ProjectedBudgetBillSensor(coordinator, entry, account))
        fpl_accounts.append(ProjectedActualBillSensor(coordinator, entry, account))
        fpl_accounts.append(DeferedAmountSensor(coordinator, entry, account))

        # usage sensors
        fpl_accounts.append(FplAverageDailySensor(coordinator, entry, account))
        fpl_accounts.append(BudgetDailyAverageSensor(coordinator, entry, account))
        fpl_accounts.append(ActualDailyAverageSensor(coordinator, entry, account))

        fpl_accounts.append(FplDailyUsageSensor(coordinator, entry, account))

        # date sensors
        fpl_accounts.append(CurrentBillDateSensor(coordinator, entry, account))
        fpl_accounts.append(NextBillDateSensor(coordinator, entry, account))
        fpl_accounts.append(ServiceDaysSensor(coordinator, entry, account))
        fpl_accounts.append(AsOfDaysSensor(coordinator, entry, account))
        fpl_accounts.append(RemainingDaysSensor(coordinator, entry, account))

        # KWH sensors
        fpl_accounts.append(ProjectedKWHSensor(coordinator, entry, account))
        fpl_accounts.append(DailyAverageKWHSensor(coordinator, entry, account))
        fpl_accounts.append(BillToDateKWHSensor(coordinator, entry, account))

    async_add_devices(fpl_accounts)
