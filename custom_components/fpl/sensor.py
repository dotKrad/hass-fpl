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
    FplDailyDeliveredReading,
    FplDailyReceivedReading,
)
from .sensor_HourlyUsageSensor import (
    FplHourlyUsageSensor,
    FplHourlyUsageKWHSensor,
    #    FplHourlyReceivedKWHSensor,
    #    FplHourlyDeliveredKWHSensor,
    #    FplHourlyReadingKWHSensor
)

from .sensor_ApplianceUsageSensor import (
    CoolingCostSensor,
    CoolingUsageSensor,
    WaterHeaterCostSensor,
    WaterHeaterUsageSensor,
    LaundryCostSensor,
    LaundryUsageSensor,
    RefrigerationCostSensor,
    RefrigerationUsageSensor,
    PoolCostSensor,
    PoolUsageSensor,
    LightingCostSensor,
    LightingUsageSensor,
    EntertainmentCostSensor,
    EntertainmentUsageSensor,
    CookingCostSensor,
    CookingUsageSensor,
    MiscellaneousCostSensor,
    MiscellaneousUsageSensor,
)


from .sensor_BalanceSensor import BalanceSensor, BalanceDueDateSensor
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
registerSensor(DailyAverageSensor, ALL_REGIONS)
registerSensor(BudgetDailyAverageSensor, ONLY_MAINREGION)
registerSensor(ActualDailyAverageSensor, ALL_REGIONS)

registerSensor(FplDailyUsageSensor, ALL_REGIONS)
registerSensor(FplDailyUsageKWHSensor, ALL_REGIONS)

# date sensors
registerSensor(CurrentBillDateSensor, ALL_REGIONS)
registerSensor(NextBillDateSensor, ALL_REGIONS)
registerSensor(ServiceDaysSensor, ALL_REGIONS)
registerSensor(AsOfDaysSensor, ALL_REGIONS)
registerSensor(RemainingDaysSensor, ALL_REGIONS)

# KWH sensors
registerSensor(ProjectedKWHSensor, ALL_REGIONS)
registerSensor(DailyAverageKWHSensor, ALL_REGIONS)
registerSensor(BillToDateKWHSensor, ALL_REGIONS)
registerSensor(NetReceivedKWHSensor, ALL_REGIONS)
registerSensor(NetDeliveredKWHSensor, ALL_REGIONS)
registerSensor(FplDailyReceivedKWHSensor, ALL_REGIONS)
registerSensor(FplDailyDeliveredKWHSensor, ALL_REGIONS)
registerSensor(FplDailyDeliveredReading, ALL_REGIONS)
registerSensor(FplDailyReceivedReading, ALL_REGIONS)

# hourly sensors
registerSensor(FplHourlyUsageSensor, ALL_REGIONS)
registerSensor(FplHourlyUsageKWHSensor, ALL_REGIONS)
# registerSensor(FplHourlyReceivedKWHSensor, ONLY_MAINREGION)
# registerSensor(FplHourlyDeliveredKWHSensor, ONLY_MAINREGION)
# registerSensor(FplHourlyReadingKWHSensor, ONLY_MAINREGION)

# Balance sensors
registerSensor(BalanceSensor, ALL_REGIONS)
registerSensor(BalanceDueDateSensor, ALL_REGIONS)

# Appliance sensors
registerSensor(CoolingCostSensor, ALL_REGIONS)
registerSensor(CoolingUsageSensor, ALL_REGIONS)
registerSensor(WaterHeaterCostSensor, ALL_REGIONS)
registerSensor(WaterHeaterUsageSensor, ALL_REGIONS)
registerSensor(LaundryCostSensor, ALL_REGIONS)
registerSensor(LaundryUsageSensor, ALL_REGIONS)
registerSensor(RefrigerationCostSensor, ALL_REGIONS)
registerSensor(RefrigerationUsageSensor, ALL_REGIONS)
registerSensor(PoolCostSensor, ONLY_MAINREGION)
registerSensor(PoolUsageSensor, ONLY_MAINREGION)
registerSensor(LightingCostSensor, ALL_REGIONS)
registerSensor(LightingUsageSensor, ALL_REGIONS)
registerSensor(EntertainmentCostSensor, ALL_REGIONS)
registerSensor(EntertainmentUsageSensor, ALL_REGIONS)
registerSensor(CookingCostSensor, ALL_REGIONS)
registerSensor(CookingUsageSensor, ALL_REGIONS)
registerSensor(MiscellaneousCostSensor, ALL_REGIONS)
registerSensor(MiscellaneousUsageSensor, ALL_REGIONS)


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
