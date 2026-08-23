"""Tests for FPL Budget Billing data fetching and sensors."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.fpl.FplMainRegionApiClient import FplMainRegionApiClient
from custom_components.fpl.sensor_ProjectedBillSensor import (
    FplProjectedBillSensor,
    DeferedAmountSensor,
    ProjectedBudgetBillSensor,
    ProjectedActualBillSensor,
    BillToDateSensor,
)
from custom_components.fpl.sensor_AverageDailySensor import (
    BudgetDailyAverageSensor,
)


class BudgetBillingApiClientTests(unittest.IsolatedAsyncioTestCase):
    """Test Budget Billing API client calculations and endpoint calls."""

    async def test_get_bbl_async_computes_projected_and_deferred_amounts(self):
        client = FplMainRegionApiClient("testuser", "testpass", None, MagicMock())
        client.jwt_token = "mock_jwt_token"

        premise_response_mock = MagicMock()
        premise_response_mock.status = 200
        premise_response_mock.json = AsyncMock(
            return_value={
                "data": {
                    "graphData": [
                        {"actuallBillAmt": 100.0},
                        {"actuallBillAmt": 120.0},
                        {"actuallBillAmt": 110.0},
                    ],
                    "defAmt": 60.0,
                }
            }
        )

        graph_response_mock = MagicMock()
        graph_response_mock.status = 200
        graph_response_mock.json = AsyncMock(
            return_value={
                "data": {
                    "eleAmt": 45.50,
                    "defAmt": 60.0,
                }
            }
        )

        client.session.get = AsyncMock(
            side_effect=[premise_response_mock, graph_response_mock]
        )

        projected_bill_data = {
            "projectedBill": 150.0,
            "as_of_days": 15,
        }

        bbl_data = await client._FplMainRegionApiClient__getBBL_async(
            "1234567890", projected_bill_data
        )

        # calc1 = (150 + (100 + 120 + 110)) / 12 = 480 / 12 = 40.0
        # calc2 = (1 / 12) * 60.0 = 5.0
        # projectedBudgetBill = 45.0
        # bbDailyAvg = round(45.0 / 30, 2) = 1.50
        # bbAsOfDateAmt = round(45.0 / 30 * 15, 2) = 22.50
        self.assertEqual(bbl_data["budget_billing_projected_bill"], 45.0)
        self.assertEqual(bbl_data["budget_billing_daily_avg"], 1.50)
        self.assertEqual(bbl_data["budget_billing_bill_to_date"], 22.50)
        self.assertEqual(bbl_data["defered_amount"], 60.0)
        self.assertEqual(bbl_data["bill_to_date"], 45.50)

    async def test_get_bbl_async_handles_partial_failure_gracefully(self):
        client = FplMainRegionApiClient("testuser", "testpass", None, MagicMock())

        premise_response_mock = MagicMock()
        premise_response_mock.status = 200
        premise_response_mock.json = AsyncMock(
            return_value={
                "data": {
                    "graphData": [{"actuallBillAmt": 50.0}],
                    "defAmt": 24.0,
                }
            }
        )

        graph_response_mock = MagicMock()
        graph_response_mock.status = 500

        client.session.get = AsyncMock(
            side_effect=[premise_response_mock, graph_response_mock]
        )

        bbl_data = await client._FplMainRegionApiClient__getBBL_async(
            "1234567890", {"projectedBill": 70.0, "as_of_days": 10}
        )

        # Premise calculation succeeds and captures defAmt even when graph endpoint fails
        self.assertEqual(bbl_data["budget_billing_projected_bill"], 12.0)
        self.assertEqual(bbl_data["defered_amount"], 24.0)

    async def test_get_data_orders_energy_usage_before_budget_billing(self):
        client = FplMainRegionApiClient("testuser", "testpass", None, MagicMock())

        account_lander_mock = MagicMock()
        account_lander_mock.status = 200
        account_lander_mock.json = AsyncMock(
            return_value={
                "data": {
                    "premiseNumber": "123456789",
                    "meterNo": "M123",
                    "currentBillDate": "2026-08-01T00:00:00",
                    "nextBillDate": "2026-08-31T00:00:00",
                    "programs": {
                        "data": [{"name": "BBL", "enrollmentStatus": "ENROLLED"}]
                    },
                }
            }
        )

        client.session.get = AsyncMock(return_value=account_lander_mock)
        client.get_energy_usage = AsyncMock(
            return_value={
                "projectedBill": 200.0,
                "billToDate": 80.0,
                "dailyAvg": 6.5,
            }
        )
        client.get_appliance_usage = AsyncMock(return_value={})
        client.get_account_details = AsyncMock(return_value={})

        passed_projected_data = {}

        async def mock_get_bbl(account, data):
            nonlocal passed_projected_data
            passed_projected_data = dict(data)
            return {
                "budget_billing_projected_bill": 180.0,
                "defered_amount": -15.0,
                "budget_billing_daily_avg": 6.0,
                "budget_billing_bill_to_date": 90.0,
            }

        client._FplMainRegionApiClient__getBBL_async = mock_get_bbl

        data = await client.update("1234567890")

        self.assertTrue(data["budget_bill"])
        self.assertEqual(passed_projected_data.get("projectedBill"), 200.0)
        self.assertEqual(data["budget_billing_projected_bill"], 180.0)
        self.assertEqual(data["defered_amount"], -15.0)


class BudgetBillingSensorTests(unittest.TestCase):
    """Test Budget Billing entity values and fallbacks."""

    def make_coordinator(self, data: dict):
        coordinator = MagicMock()
        coordinator.data = {"1234567890": data}
        return coordinator

    def test_budget_billing_sensors_populate_correctly(self):
        coordinator = self.make_coordinator(
            {
                "budget_bill": True,
                "budget_billing_projected_bill": 180.0,
                "defered_amount": 42.50,
                "budget_billing_daily_avg": 6.0,
                "budget_billing_bill_to_date": 90.0,
                "projectedBill": 210.0,
                "billToDate": 95.0,
            }
        )

        proj_budget_sensor = ProjectedBudgetBillSensor(
            coordinator, None, "1234567890"
        )
        deferred_sensor = DeferedAmountSensor(coordinator, None, "1234567890")
        budget_daily_avg_sensor = BudgetDailyAverageSensor(
            coordinator, None, "1234567890"
        )
        proj_bill_sensor = FplProjectedBillSensor(coordinator, None, "1234567890")
        proj_actual_sensor = ProjectedActualBillSensor(coordinator, None, "1234567890")
        bill_to_date_sensor = BillToDateSensor(coordinator, None, "1234567890")

        self.assertEqual(proj_budget_sensor.native_value, 180.0)
        self.assertEqual(deferred_sensor.native_value, 42.50)
        self.assertEqual(budget_daily_avg_sensor.native_value, 6.0)
        self.assertEqual(proj_bill_sensor.native_value, 180.0)
        self.assertTrue(proj_bill_sensor.customAttributes()["budget_bill"])
        self.assertEqual(proj_actual_sensor.native_value, 210.0)
        self.assertEqual(bill_to_date_sensor.native_value, 90.0)

    def test_budget_billing_sensors_graceful_when_not_enrolled(self):
        coordinator = self.make_coordinator(
            {
                "budget_bill": False,
                "projectedBill": 210.0,
                "billToDate": 95.0,
            }
        )

        deferred_sensor = DeferedAmountSensor(coordinator, None, "1234567890")
        proj_budget_sensor = ProjectedBudgetBillSensor(
            coordinator, None, "1234567890"
        )
        proj_bill_sensor = FplProjectedBillSensor(coordinator, None, "1234567890")
        bill_to_date_sensor = BillToDateSensor(coordinator, None, "1234567890")

        self.assertIsNone(deferred_sensor.native_value)
        self.assertIsNone(proj_budget_sensor.native_value)
        self.assertEqual(proj_bill_sensor.native_value, 210.0)
        self.assertEqual(bill_to_date_sensor.native_value, 95.0)


if __name__ == "__main__":
    unittest.main()
