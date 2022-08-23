"""Sensor platform for integration_blueprint."""

from .sensor_KWHSensor import (
    ProjectedKWHSensor,
    DailyAverageKWHSensor,
    BillToDateKWHSensor,
    NetReceivedKWHSensor,
    NetDeliveredKWHSensor,
)
from .sensor_DatesSensor import (
    CurrentBillDateSensor,
    NextBillDateSensor,
    ServiceDaysSensor,
    AsOfDaysSensor,
    RemainingDaysSensor,
)
from .sensor_ProjectedBillSensor import (
    BillToDateSensor,
    FplProjectedBillSensor,
    ProjectedBudgetBillSensor,
    ProjectedActualBillSensor,
    DeferedAmountSensor,
)
from .sensor_AverageDailySensor import (
    DailyAverageSensor,
    BudgetDailyAverageSensor,
    ActualDailyAverageSensor,
)
from .sensor_DailyUsageSensor import (
    FplDailyUsageKWHSensor,
    FplDailyUsageSensor,
    FplDailyDeliveredKWHSensor,
    FplDailyReceivedKWHSensor,
)

from .const import CONF_ACCOUNTS, CONF_TERRITORY, DOMAIN, FPL_MAINREGION, FPL_NORTHWEST

ALL_REGIONS = [FPL_MAINREGION, FPL_NORTHWEST]
ONLY_MAINREGION = [FPL_MAINREGION]

sensors = {}


def registerSensor(sensor, regions):
    """register all available sensors"""
    for region in regions:
        if region in sensors:
            sensors[region].append(sensor)
        else:
            sensors[region] = [sensor]


# bill sensors
registerSensor(FplProjectedBillSensor, ALL_REGIONS)
registerSensor(BillToDateSensor, ALL_REGIONS)

# budget billing
registerSensor(ProjectedBudgetBillSensor, ONLY_MAINREGION)
registerSensor(ProjectedActualBillSensor, ONLY_MAINREGION)
registerSensor(DeferedAmountSensor, ONLY_MAINREGION)


# usage sensors
registerSensor(DailyAverageSensor, ONLY_MAINREGION)
registerSensor(BudgetDailyAverageSensor, ONLY_MAINREGION)
registerSensor(ActualDailyAverageSensor, ONLY_MAINREGION)

registerSensor(FplDailyUsageSensor, ONLY_MAINREGION)
registerSensor(FplDailyUsageKWHSensor, ONLY_MAINREGION)

# date sensors
registerSensor(CurrentBillDateSensor, ALL_REGIONS)
registerSensor(NextBillDateSensor, ONLY_MAINREGION)
registerSensor(ServiceDaysSensor, ALL_REGIONS)
registerSensor(AsOfDaysSensor, ALL_REGIONS)
registerSensor(RemainingDaysSensor, ALL_REGIONS)

# KWH sensors
registerSensor(ProjectedKWHSensor, ALL_REGIONS)
registerSensor(DailyAverageKWHSensor, ONLY_MAINREGION)
registerSensor(BillToDateKWHSensor, ALL_REGIONS)
registerSensor(NetReceivedKWHSensor, ONLY_MAINREGION)
registerSensor(NetDeliveredKWHSensor, ONLY_MAINREGION)
registerSensor(FplDailyReceivedKWHSensor, ONLY_MAINREGION)
registerSensor(FplDailyDeliveredKWHSensor, ONLY_MAINREGION)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""

    accounts = entry.data.get(CONF_ACCOUNTS)
    territory = entry.data.get(CONF_TERRITORY)

    coordinator = hass.data[DOMAIN][entry.entry_id]
    fpl_accounts = []

    for account in accounts:
        for sensor in sensors[territory]:
            fpl_accounts.append(sensor(coordinator, entry, account))

    async_add_devices(fpl_accounts)
