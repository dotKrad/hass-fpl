"""FPL Northwest / Gulf region API client."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

import async_timeout

from .const import (
    API_HOST,
    LOGIN_RESULT_FAILURE,
    LOGIN_RESULT_INVALIDPASSWORD,
    LOGIN_RESULT_OK,
)

_LOGGER = logging.getLogger(__package__)

COGNITO_URL = "https://cognito-idp.us-east-1.amazonaws.com"
NW_COGNITO_CLIENT_ID = "1dt9rk4cta0ts8obgrs2sef4s3"
NW_REQUEST_TIMEOUT = 30

ACCOUNT_STATUS_ACTIVE = "ACT"

URL_ACCOUNTS_LIST = API_HOST + "/cs/gulf/ssp/v1/profile/accounts/list"
URL_REM_ACCOUNT_SUMMARY = (
    API_HOST + "/cs/gulf/ssp/v1/rem/resources/account/{account}/account-summary"
)
URL_LIVE_ACCOUNT_SUMMARY = (
    API_HOST
    + "/cs/gulf/ssp/v1/accountservices/account/{account}/accountSummary?balance=n"
)
URL_MONTHLY_USAGE = (
    API_HOST
    + "/cs/gulf/ssp/v1/accountservices/account/{account}/monthlyUsage?contractId={contract_id}"
)
URL_DISAGGREGATION = (
    API_HOST
    + "/cs/gulf/ssp/v1/rem/resources/customer/accounts/{account}/get-disagg"
)

ACTIVE_ACCOUNT_STATUSES = {ACCOUNT_STATUS_ACTIVE, "ACT", "Active", "active"}


class FplNorthwestRegionApiClient:
    """FPL Northwest (Gulf / SSP) API client."""

    def __init__(
        self,
        username,
        password,
        loop,
        session,
        configured_accounts: list[str] | None = None,
    ) -> None:
        self.session = session
        self.username = (username or "").strip().lower()
        self.password = password
        self.loop = loop
        self.id_token = None
        self.access_token = None
        self._configured_accounts = [
            str(account).strip() for account in (configured_accounts or []) if account
        ]

    def _api_headers(self) -> dict[str, str]:
        return {
            "accept": "application/json, text/plain, */*",
            "authorization": f"Bearer {self.id_token}",
            "accesstoken": self.access_token,
            "jwttoken": self.id_token,
            "x-param-channel": "web",
        }

    async def _request(
        self, method: str, url: str, *, headers: dict | None = None, json_payload=None
    ):
        request_headers = headers or {}
        try:
            async with async_timeout.timeout(NW_REQUEST_TIMEOUT):
                if method == "POST":
                    response = await self.session.post(
                        url, headers=request_headers, json=json_payload
                    )
                else:
                    response = await self.session.get(url, headers=request_headers)

            if response.status != 200:
                _LOGGER.debug(
                    "NW %s %s returned HTTP %s", method, url, response.status
                )
                return None

            return await response.json(content_type=None)
        except Exception as err:
            _LOGGER.debug("NW %s %s failed: %s", method, url, err)
            return None

    async def login(self):
        """Authenticate with Cognito using the Gulf web client."""
        cognito_headers = {
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
        }
        auth_payload = {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": NW_COGNITO_CLIENT_ID,
            "AuthParameters": {
                "USERNAME": self.username,
                "PASSWORD": self.password,
            },
        }

        try:
            async with async_timeout.timeout(NW_REQUEST_TIMEOUT):
                response = await self.session.post(
                    COGNITO_URL, headers=cognito_headers, json=auth_payload
                )
        except Exception as err:
            _LOGGER.error("NW Cognito login failed: %s", err)
            return LOGIN_RESULT_FAILURE

        if response.status != 200:
            body = await response.text()
            _LOGGER.debug("NW Cognito login HTTP %s: %s", response.status, body)
            if "NotAuthorizedException" in body or "Incorrect username or password" in body:
                return LOGIN_RESULT_INVALIDPASSWORD
            return LOGIN_RESULT_FAILURE

        auth_data = await response.json(content_type=None)
        auth_result = auth_data.get("AuthenticationResult") or {}
        self.access_token = auth_result.get("AccessToken")
        self.id_token = auth_result.get("IdToken")

        if not self.access_token or not self.id_token:
            return LOGIN_RESULT_FAILURE

        return LOGIN_RESULT_OK

    def _accounts_from_payload(self, payload) -> list[str]:
        if not isinstance(payload, dict):
            return []

        accounts = payload.get("accounts")
        if accounts is None and isinstance(payload.get("data"), dict):
            accounts = payload["data"].get("accounts")

        if not isinstance(accounts, list):
            return []

        result: list[str] = []
        for account in accounts:
            if not isinstance(account, dict):
                continue
            status = account.get("accountStatus") or account.get("status")
            number = account.get("accountNumber") or account.get("account")
            if number and (status is None or status in ACTIVE_ACCOUNT_STATUSES):
                result.append(str(number))
        return result

    async def get_open_accounts(self):
        """Return active accounts from the Gulf profile API or configured fallback."""
        if not self.id_token:
            await self.login()

        payload = await self._request(
            "GET", URL_ACCOUNTS_LIST, headers=self._api_headers()
        )
        accounts = self._accounts_from_payload(payload)
        if accounts:
            return accounts

        if self._configured_accounts:
            return list(self._configured_accounts)

        return []

    async def logout(self):
        """Log out from FPL."""

    async def get_hourly_usage(self, account, premise, date) -> list:
        """Hourly usage is not available for the Gulf SSP API yet."""
        return []

    async def update(self, account):
        """Collect account data from Gulf SSP endpoints."""
        if not self.id_token:
            await self.login()

        headers = self._api_headers()
        result: dict = {"budget_bill": False}

        rem_summary = await self._request(
            "GET", URL_REM_ACCOUNT_SUMMARY.format(account=account), headers=headers
        )
        if isinstance(rem_summary, dict):
            result["premise"] = rem_summary.get("premiseNumber")
            result["contract_id"] = rem_summary.get("contractId")

        contract_id = result.get("contract_id")
        premise_id = result.get("premise")

        now = datetime.now()
        from_date = (now - timedelta(days=35)).strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")
        disagg_body = {
            "accountNumber": str(account),
            "contractId": str(contract_id or ""),
            "premiseId": str(premise_id or ""),
            "fromDate": from_date,
            "toDate": to_date,
        }

        tasks = [
            self._request(
                "GET",
                URL_LIVE_ACCOUNT_SUMMARY.format(account=account),
                headers=headers,
            )
        ]
        if contract_id:
            tasks.append(
                self._request(
                    "GET",
                    URL_MONTHLY_USAGE.format(account=account, contract_id=contract_id),
                    headers=headers,
                )
            )
        if contract_id and premise_id:
            tasks.append(
                self._request(
                    "POST",
                    URL_DISAGGREGATION.format(account=account),
                    headers=headers,
                    json_payload=disagg_body,
                )
            )

        responses = await asyncio.gather(*tasks)
        live_summary = responses[0] if responses else None
        monthly_data = responses[1] if len(responses) > 1 else None
        disagg_data = responses[2] if len(responses) > 2 else None

        result.update(self._map_live_summary(live_summary))
        result.update(self._map_monthly_usage(monthly_data))
        result.update(self._map_disaggregation(disagg_data))

        return result

    def _map_live_summary(self, payload: dict | None) -> dict:
        mapped: dict = {}
        if not isinstance(payload, dict):
            return mapped

        summary = payload.get("accountSummary", {})
        summary_data = summary.get("accountSummaryData", {})
        bill_info = summary_data.get("billAndMeterInfo", {}) or {}
        program_info = summary_data.get("programInfo", {}) or {}

        if bill_info.get("projBillAmount") is not None:
            mapped["projectedBill"] = float(bill_info["projBillAmount"])
        if bill_info.get("projBillKWH") is not None:
            mapped["projectedKWH"] = int(bill_info["projBillKWH"])
        if bill_info.get("asOfDateAmount") is not None:
            mapped["billToDate"] = float(bill_info["asOfDateAmount"])
        if bill_info.get("asOfDateUsage") is not None:
            mapped["billToDateKWH"] = int(bill_info["asOfDateUsage"])
        if bill_info.get("dailyAvgAmount") is not None:
            mapped["dailyAvg"] = float(bill_info["dailyAvgAmount"])
        if bill_info.get("dailyAvgKwh") is not None:
            mapped["dailyAverageKWH"] = int(bill_info["dailyAvgKwh"])

        today_raw = payload.get("today")
        current_bill = program_info.get("currentBillDate")
        next_bill = program_info.get("nextBillDate")

        if current_bill:
            start = self._parse_date(current_bill)
            if start:
                mapped["current_bill_date"] = start.strftime("%Y-%m-%d")
        if next_bill:
            mapped["next_bill_date"] = next_bill

        if current_bill and next_bill:
            start = self._parse_date(current_bill)
            end = self._parse_date(next_bill)
            today = self._parse_date(today_raw) or datetime.now()
            if start and end:
                service_days = (end - start).days
                as_of_days = max((today - start).days, 0)
                mapped["service_days"] = service_days
                mapped["as_of_days"] = as_of_days
                mapped["remaining_days"] = max(service_days - as_of_days, 0)

        return mapped

    def _map_monthly_usage(self, payload: dict | None) -> dict:
        mapped: dict = {}
        if not isinstance(payload, dict):
            return mapped

        results = payload.get("results") or []
        if not results:
            return mapped

        latest = results[0]
        if latest.get("billedConsKwh") is not None:
            mapped["last_cycle_kwh"] = int(latest["billedConsKwh"])
        if latest.get("actualBillAmount") is not None:
            mapped["last_cycle_bill"] = float(latest["actualBillAmount"])
        return mapped

    def _map_disaggregation(self, payload: dict | None) -> dict:
        if not isinstance(payload, dict):
            return {}

        bill_periods = payload.get("data", {}).get("billPeriods", [])
        if not bill_periods:
            return {}

        period = bill_periods[0]
        return {
            "appliance_usage": {
                "categories": period.get("categories") or [],
                "startDate": period.get("startDate") or period.get("fromDate"),
                "endDate": period.get("endDate") or period.get("toDate"),
            }
        }

    @staticmethod
    def _parse_date(value) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        text = str(value).strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            for fmt in ("%m-%d-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    continue
        return None
