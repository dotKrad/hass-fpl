"""Data Update Coordinator"""

import asyncio
import logging
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    StatisticData,
    StatisticMetaData,
    statistics_during_period,
)
from homeassistant.core import HomeAssistant
from homeassistant.components import recorder

from homeassistant.util import dt as dt_util

from .fplapi import FplApi
from .const import DOMAIN, CONF_ACCOUNTS

# FPL operates in Florida, which is in the Eastern timezone
FPL_TIMEZONE = ZoneInfo("America/New_York")

SCAN_INTERVAL = timedelta(seconds=1200)
# Anything more than 15 days may cause Cloudflare to block all of our requests.
HOURLY_USAGE_BACKFILL_DAYS = 15
HOURLY_USAGE_START_HOUR = 4

_LOGGER: logging.Logger = logging.getLogger(__package__)


def _fpl_read_time(read_time: datetime) -> datetime:
    """Return an FPL reading time in FPL's timezone."""
    if read_time.tzinfo is None:
        return read_time.replace(tzinfo=FPL_TIMEZONE)
    return read_time.astimezone(FPL_TIMEZONE)


def _is_hourly_day_complete(hourly: list, target_date: date) -> bool:
    """Return whether hourly data contains the day's closing interval."""
    expected_end = datetime.combine(
        target_date + timedelta(days=1), time.min, FPL_TIMEZONE
    )
    return any(
        (read_time := hour.get("readTime")) is not None
        and _fpl_read_time(read_time) == expected_end
        for hour in hourly
    )


class FplDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: FplApi) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []
        self._hourly_backfill_pending = True
        self._finalized_hourly_dates: set[tuple[str, date]] = set()

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _get_sum_before(self, stat_id: str, start: datetime) -> float:
        def _read():
            return statistics_during_period(
                self.hass,
                start - timedelta(hours=1),
                start,
                {stat_id},
                "hour",
                None,
                types={"sum"},
            )

        result = await recorder.get_instance(self.hass).async_add_executor_job(_read)

        if rows := result.get(stat_id):
            return float(rows[-1]["sum"] or 0.0)
        return 0.0

    async def _publish_hourly_statistics(self, account: str, hourly: list) -> None:
        stat_id_usage = f"{DOMAIN}:{account}_hourly_usage"
        stat_id_cost = f"{DOMAIN}:{account}_hourly_cost"

        normalized = []
        for hour in hourly:
            read_time = hour.get("readTime")
            if read_time is None:
                continue
            read_time_utc = _fpl_read_time(read_time).astimezone(dt_util.UTC)
            read_time_utc = read_time_utc.replace(minute=0, second=0, microsecond=0)
            normalized.append((read_time_utc - timedelta(hours=1), hour))

        if not normalized:
            return

        normalized.sort(key=lambda item: item[0])
        first_start = normalized[0][0]
        usage_sum = await self._get_sum_before(stat_id_usage, first_start)
        cost_sum = await self._get_sum_before(stat_id_cost, first_start)

        cost_stats = []
        usage_stats = []
        for start, h in normalized:
            cost = h.get("billingCharged")
            usage = h.get("kwhActual")

            if cost is not None:
                cost_sum += cost
                cost_stats.append(StatisticData(start=start, sum=cost_sum, state=cost))

            if usage is not None:
                usage_sum += usage
                usage_stats.append(
                    StatisticData(start=start, sum=usage_sum, state=usage)
                )

        if cost_stats:
            metadata = StatisticMetaData(
                has_mean=False,
                has_sum=True,
                source=DOMAIN,
                name=f"FPL {account} Hourly Cost",
                statistic_id=stat_id_cost,
                unit_of_measurement="USD",
            )

            async_add_external_statistics(self.hass, metadata, cost_stats)

        if usage_stats:
            metadata = StatisticMetaData(
                has_mean=False,
                has_sum=True,
                source=DOMAIN,
                name=f"FPL {account} Hourly Usage",
                statistic_id=stat_id_usage,
                unit_of_measurement="kWh",
            )

            async_add_external_statistics(self.hass, metadata, usage_stats)

        return cost_sum, usage_sum

    async def _async_update_data(self):
        try:
            data = await self.api.async_get_data()
            now = dt_util.now().astimezone(FPL_TIMEZONE)
            if now.hour < HOURLY_USAGE_START_HOUR:
                return data

            yesterday = now.date() - timedelta(days=1)
            is_backfill = self._hourly_backfill_pending
            if is_backfill:
                target_dates = [
                    now.date() - timedelta(days=offset)
                    for offset in range(HOURLY_USAGE_BACKFILL_DAYS, 0, -1)
                ]
            else:
                target_dates = [yesterday]

            accounts = data.get(CONF_ACCOUNTS, [])
            backfill_complete = bool(accounts)
            for account in accounts:
                premise = data.get(account, {}).get("premise")
                complete_dates = []
                all_hourly = []
                for target_date in target_dates:
                    if (
                        not is_backfill
                        and (account, target_date) in self._finalized_hourly_dates
                    ):
                        continue
                    hourly = await self.api.apiClient.get_hourly_usage(
                        account, premise, target_date
                    )
                    if _is_hourly_day_complete(hourly, target_date):
                        all_hourly.extend(hourly)
                        complete_dates.append(target_date)
                    if len(target_dates) > 1:
                        await asyncio.sleep(1)

                if is_backfill and len(complete_dates) != len(target_dates):
                    backfill_complete = False
                    continue

                if all_hourly:
                    await self._publish_hourly_statistics(account, all_hourly)
                    self._finalized_hourly_dates.update(
                        (account, target_date) for target_date in complete_dates
                    )

            if is_backfill:
                self._hourly_backfill_pending = not backfill_complete

            return data
        except Exception as exception:
            raise UpdateFailed() from exception
