"""Tests for FPL hourly statistics finalization."""

import unittest
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from custom_components.fpl import fplDataUpdateCoordinator as coordinator_module
from custom_components.fpl.const import CONF_ACCOUNTS
from custom_components.fpl.fplDataUpdateCoordinator import (
    FPL_TIMEZONE,
    HOURLY_USAGE_BACKFILL_DAYS,
    FplDataUpdateCoordinator,
)


def hourly_day(target_date: date, *, complete: bool) -> list[dict]:
    """Return representative FPL hourly data."""
    hours = 24 if complete else 23
    start = datetime.combine(target_date, datetime.min.time())
    return [
        {
            "readTime": start + timedelta(hours=hour),
            "kwhActual": 0.0 if hour == 21 else 1.0,
            "billingCharged": 0.1,
        }
        for hour in range(1, hours + 1)
    ]


class HourlyCompletionTests(unittest.TestCase):
    """Test FPL day completion detection."""

    def test_requires_closing_interval_but_allows_zero_usage(self):
        target_date = date(2026, 7, 26)
        is_complete = getattr(coordinator_module, "_is_hourly_day_complete", None)

        self.assertTrue(callable(is_complete), "completion helper is missing")
        self.assertFalse(
            is_complete(hourly_day(target_date, complete=False), target_date)
        )
        self.assertTrue(
            is_complete(hourly_day(target_date, complete=True), target_date)
        )


class HourlyPublishingTests(unittest.IsolatedAsyncioTestCase):
    """Test correction of previously imported hourly statistics."""

    async def test_republishes_existing_hours_from_preceding_sum(self):
        coordinator = object.__new__(FplDataUpdateCoordinator)
        coordinator.hass = object()
        coordinator._get_last_sum = AsyncMock(
            return_value=(
                999.0,
                datetime(2026, 7, 27, 4, tzinfo=coordinator_module.dt_util.UTC),
            )
        )
        coordinator._get_sum_before = AsyncMock(
            side_effect=lambda statistic_id, _start: (
                100.0 if statistic_id.endswith("_hourly_usage") else 50.0
            )
        )
        hourly = [
            {
                "readTime": datetime(2026, 7, 26, 21),
                "kwhActual": 2.0,
                "billingCharged": 0.2,
            },
            {
                "readTime": datetime(2026, 7, 26, 22),
                "kwhActual": 3.0,
                "billingCharged": 0.3,
            },
        ]

        with patch.object(
            coordinator_module, "async_add_external_statistics"
        ) as add_statistics:
            await coordinator._publish_hourly_statistics("account", hourly)

        calls_by_id = {
            call.args[1]["statistic_id"]: call.args[2]
            for call in add_statistics.call_args_list
        }
        self.assertIn("fpl:account_hourly_usage", calls_by_id)
        self.assertIn("fpl:account_hourly_cost", calls_by_id)
        usage = calls_by_id["fpl:account_hourly_usage"]
        cost = calls_by_id["fpl:account_hourly_cost"]
        self.assertEqual([row["state"] for row in usage], [2.0, 3.0])
        self.assertEqual([row["sum"] for row in usage], [102.0, 105.0])
        self.assertEqual([row["sum"] for row in cost], [50.2, 50.5])


class HourlySchedulingTests(unittest.IsolatedAsyncioTestCase):
    """Test retry and startup repair scheduling."""

    def make_coordinator(self, hourly_response) -> FplDataUpdateCoordinator:
        coordinator = object.__new__(FplDataUpdateCoordinator)
        coordinator.api = SimpleNamespace(
            async_get_data=AsyncMock(
                return_value={
                    CONF_ACCOUNTS: ["account"],
                    "account": {"premise": "premise"},
                }
            ),
            apiClient=SimpleNamespace(get_hourly_usage=AsyncMock()),
        )
        coordinator.api.apiClient.get_hourly_usage.side_effect = hourly_response
        coordinator._publish_hourly_statistics = AsyncMock()
        coordinator._get_last_sum = AsyncMock(
            return_value=(1.0, datetime(2026, 7, 26, tzinfo=FPL_TIMEZONE))
        )
        coordinator._hourly_backfill_pending = False
        coordinator._finalized_hourly_dates = set()
        return coordinator

    async def test_retries_incomplete_day_then_stops_after_finalized_import(self):
        target_date = date(2026, 7, 26)
        responses = [
            hourly_day(target_date, complete=False),
            hourly_day(target_date, complete=True),
        ]
        coordinator = self.make_coordinator(lambda *_: responses.pop(0))

        with patch.object(
            coordinator_module.dt_util,
            "now",
            return_value=datetime(2026, 7, 27, 4, tzinfo=FPL_TIMEZONE),
        ):
            await coordinator._async_update_data()
            self.assertEqual(coordinator._publish_hourly_statistics.await_count, 0)

            await coordinator._async_update_data()
            self.assertEqual(coordinator._publish_hourly_statistics.await_count, 1)

            await coordinator._async_update_data()

        self.assertEqual(coordinator.api.apiClient.get_hourly_usage.await_count, 2)
        self.assertEqual(coordinator._publish_hourly_statistics.await_count, 1)

    async def test_repairs_recent_window_only_once_per_startup(self):
        today = date(2026, 7, 27)
        coordinator = self.make_coordinator(
            lambda _account, _premise, target: hourly_day(
                target if isinstance(target, date) else target.date(),
                complete=True,
            )
        )
        coordinator._hourly_backfill_pending = True

        with (
            patch.object(
                coordinator_module.dt_util,
                "now",
                return_value=datetime(2026, 7, 27, 4, tzinfo=FPL_TIMEZONE),
            ),
            patch.object(coordinator_module.asyncio, "sleep", new=AsyncMock()),
        ):
            await coordinator._async_update_data()
            await coordinator._async_update_data()

        self.assertEqual(
            coordinator.api.apiClient.get_hourly_usage.await_count,
            HOURLY_USAGE_BACKFILL_DAYS,
        )
        requested_dates = {
            call.args[2]
            for call in coordinator.api.apiClient.get_hourly_usage.await_args_list
        }
        self.assertEqual(
            requested_dates,
            {
                today - timedelta(days=offset)
                for offset in range(1, HOURLY_USAGE_BACKFILL_DAYS + 1)
            },
        )


if __name__ == "__main__":
    unittest.main()
