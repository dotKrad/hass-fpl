"""FPL Northwest / Gulf region API client."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import date, datetime, timedelta

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
URL_LIVE_ACCOUNT_SUMMARY_BALANCE = (
    API_HOST
    + "/cs/gulf/ssp/v1/accountservices/account/{account}/accountSummary?balance=y"
)
URL_ACCOUNT_LITE_INFO = (
    API_HOST + "/cs/customer/v3/accountservices/resources/accounts/{account}/lite-info"
)
URL_BILLING_HISTORY = (
    API_HOST
    + "/cs/customer/v3/account-summary/resources/accounts/bill-histories/{account}"
)
URL_MONTHLY_USAGE = (
    API_HOST
    + "/cs/gulf/ssp/v1/accountservices/account/{account}/monthlyUsage?contractId={contract_id}"
)
URL_DISAGGREGATION = (
    API_HOST + "/cs/gulf/ssp/v1/rem/resources/customer/accounts/{account}/get-disagg"
)
URL_DAILY_USAGE = (
    API_HOST + "/cs/gulf/ssp/v1/accountservices/account/{account}/daily-usage"
)
URL_HOURLY_USAGE = (
    API_HOST + "/cs/gulf/ssp/v1/accountservices/account/{account}/hourly-usage"
)
URL_MOBILE_HOURLY_USAGE = (
    API_HOST
    + "/cs/customer/v1/energydashboard/resources/energy-usage/account/{account}/mobile-hourly-usage"
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
        self._account_context: dict[str, dict] = {}

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
                _LOGGER.debug("NW %s %s returned HTTP %s", method, url, response.status)
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
            if (
                "NotAuthorizedException" in body
                or "Incorrect username or password" in body
            ):
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
        """Fetch hourly usage for Energy Dashboard statistics backfill."""
        if not self.id_token:
            await self.login()

        headers = self._api_headers()
        ctx = self._account_context.get(account, {})
        meter_id = ctx.get("meter_id")
        target_date = date.strftime("%Y-%m-%d")

        if meter_id:
            gulf_url = (
                f"{URL_HOURLY_USAGE.format(account=account)}"
                f"?date={target_date}&meterId={meter_id}"
            )
            gulf_payload = await self._request("GET", gulf_url, headers=headers)
            parsed = self._parse_hourly_payload(gulf_payload)
            if parsed:
                return parsed

        if premise:
            mobile_payload = {
                "premiseNumber": premise,
                "startDate": date.strftime("%m-%d-%Y"),
                "endDate": date.strftime("%m-%d-%Y"),
            }
            mobile_response = await self._request(
                "POST",
                URL_MOBILE_HOURLY_USAGE.format(account=account),
                headers=headers,
                json_payload=mobile_payload,
            )
            parsed = self._parse_hourly_payload(mobile_response)
            if parsed:
                return parsed

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
        contract_id = None
        premise_id = None
        if isinstance(rem_summary, dict):
            contract_id = rem_summary.get("contractId")
            premise_id = rem_summary.get("premiseNumber")
            result["premise"] = premise_id
            result["contract_id"] = contract_id
            result["meterNo"] = rem_summary.get("meterNumber")

        self._account_context[account] = {
            "premise": premise_id,
            "contract_id": contract_id,
            "meter_id": (
                rem_summary.get("meterNumber")
                if isinstance(rem_summary, dict)
                else None
            ),
            "zip_code": None,
        }

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

        tasks = {
            "live_summary": self._request(
                "GET",
                URL_LIVE_ACCOUNT_SUMMARY.format(account=account),
                headers=headers,
            ),
            "balance_summary": self._request(
                "GET",
                URL_LIVE_ACCOUNT_SUMMARY_BALANCE.format(account=account),
                headers=headers,
            ),
            "lite_info": self._request(
                "GET",
                URL_ACCOUNT_LITE_INFO.format(account=account),
                headers=headers,
            ),
            "billing_history": self._request(
                "GET",
                URL_BILLING_HISTORY.format(account=account),
                headers=headers,
            ),
        }
        if contract_id:
            tasks["monthly"] = self._request(
                "GET",
                URL_MONTHLY_USAGE.format(account=account, contract_id=contract_id),
                headers=headers,
            )
        if contract_id and premise_id:
            tasks["disagg"] = self._request(
                "POST",
                URL_DISAGGREGATION.format(account=account),
                headers=headers,
                json_payload=disagg_body,
            )

        task_names = list(tasks.keys())
        responses = await asyncio.gather(*tasks.values())
        payload = dict(zip(task_names, responses))

        live_summary = payload.get("live_summary")
        lite_info = payload.get("lite_info")

        zip_code = self._zip_from_lite_info(lite_info)
        if zip_code:
            self._account_context[account]["zip_code"] = zip_code

        result.update(self._map_live_summary(live_summary))
        result.update(
            self._map_balance(
                payload.get("balance_summary"), payload.get("billing_history")
            )
        )
        result.update(self._map_monthly_usage(payload.get("monthly")))
        result.update(self._map_disaggregation(payload.get("disagg")))

        daily_usage_url = self._build_daily_usage_url(account, live_summary)
        if daily_usage_url:
            daily_payload = await self._request("GET", daily_usage_url, headers=headers)
            result.update(self._map_daily_usage(daily_payload))

        return result

    def _zip_from_lite_info(self, payload: dict | None) -> str | None:
        if not isinstance(payload, dict):
            return None
        service_address = payload.get("data", {}).get("serviceAddress", {})
        return service_address.get("zipcode") or service_address.get("zip")

    def _build_daily_usage_url(
        self, account: str, live_summary: dict | None
    ) -> str | None:
        if not isinstance(live_summary, dict):
            return None

        ctx = self._account_context.get(account, {})
        meter_id = ctx.get("meter_id")
        zip_code = ctx.get("zip_code")
        if not meter_id or not zip_code:
            return None

        summary_data = live_summary.get("accountSummary", {}).get(
            "accountSummaryData", {}
        )
        bill_info = summary_data.get("billAndMeterInfo", {}) or {}
        program_info = summary_data.get("programInfo", {}) or {}

        start = self._parse_date(program_info.get("currentBillDate"))
        end = self._parse_date(program_info.get("nextBillDate"))
        if not start or not end:
            return None

        service_days = max((end - start).days, 1)
        minimum_charge = (
            bill_info.get("projBaseCharge") or bill_info.get("minimumCharge") or 0
        )
        bill_amount = (
            bill_info.get("asOfDateAmount") or bill_info.get("projBillAmount") or 0
        )
        total_kwh = bill_info.get("asOfDateUsage") or bill_info.get("projBillKWH") or 0

        return (
            f"{URL_DAILY_USAGE.format(account=account)}"
            f"?startDate={start.strftime('%Y-%m-%d')}"
            f"&endDate={end.strftime('%Y-%m-%d')}"
            f"&serviceDays={service_days}"
            f"&meterId={meter_id}"
            f"&minimumCharge={minimum_charge}"
            f"&billAmount={bill_amount}"
            f"&totalKwhConsumed={total_kwh}"
            f"&zipCode={zip_code}"
        )

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

        for src, dest in (
            ("recMtrReading", "recMtrReading"),
            ("delMtrReading", "delMtrReading"),
            ("receivedKwh", "recMtrReading"),
            ("deliveredKwh", "delMtrReading"),
        ):
            if bill_info.get(src) is not None and dest not in mapped:
                mapped[dest] = int(bill_info[src])

        mapped["net_meter"] = bill_info.get("netMeterFlag") in (
            True,
            "Y",
            "y",
            "true",
            1,
        )

        today_raw = payload.get("today")
        current_bill = program_info.get("currentBillDate")
        next_bill = program_info.get("nextBillDate")

        if current_bill:
            start = self._parse_date(current_bill)
            if start:
                mapped["current_bill_date"] = start.strftime("%Y-%m-%d")
        if next_bill:
            end = self._parse_date(next_bill)
            if end:
                mapped["next_bill_date"] = end.strftime("%Y-%m-%d")

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

    def _map_balance(
        self, balance_summary: dict | None, billing_history: dict | None
    ) -> dict:
        mapped: dict = {}

        if isinstance(balance_summary, dict):
            summary_data = balance_summary.get("accountSummary", {}).get(
                "accountSummaryData", {}
            )
            balance_info = (
                summary_data.get("balanceInfo")
                or summary_data.get("billAndMeterInfo")
                or {}
            )
            for key in ("amountDue", "balanceDue", "currentBalance", "actualBalance"):
                if balance_info.get(key) is not None:
                    mapped["balance"] = float(balance_info[key])
                    break
            due_raw = balance_info.get("dueDate") or balance_info.get("paymentDueDate")
            due_date = self._parse_date(due_raw)
            if due_date:
                mapped["balance_due_date"] = due_date.date()

        if isinstance(billing_history, dict):
            results = billing_history.get("data", {}).get("results", [])
            if results and isinstance(results, list):
                latest = results[0]
                if "balance" not in mapped:
                    amount = latest.get("amountDue") or latest.get("totalAmount")
                    if amount is not None:
                        mapped["balance"] = float(
                            str(amount).replace("$", "").replace(",", "")
                        )
                if "balance_due_date" not in mapped:
                    due_text = self._parse_fpl_date(latest.get("dueDate"))
                    if due_text:
                        try:
                            mapped["balance_due_date"] = datetime.strptime(
                                due_text, "%Y-%m-%d"
                            ).date()
                        except ValueError:
                            pass

        return mapped

    def _map_daily_usage(self, payload: dict | None) -> dict:
        if not isinstance(payload, dict):
            return {}

        reads = payload.get("dailyMeterReads") or []
        if not reads:
            return {}

        latest = max(reads, key=lambda row: row.get("date", ""))
        read_day = self._parse_date(latest.get("date"))
        if read_day is None:
            return {}

        read_time = read_day + timedelta(days=1)
        billed_kwh = float(latest.get("billedConsKwh") or 0)
        diff_kwh = float(latest.get("diffConsKwh") or 0)

        daily_usage = {
            "kwhActual": billed_kwh,
            "billingCharge": float(latest.get("billedConsAmt") or 0),
            "readTime": read_time,
            "reading": float(latest.get("kwhRead") or 0),
        }

        if diff_kwh < 0:
            daily_usage["netDeliveredKwh"] = abs(diff_kwh)
        else:
            daily_usage["netDeliveredKwh"] = billed_kwh
            daily_usage["netDeliveredReading"] = float(latest.get("kwhRead") or 0)

        return {"DailyUsage": daily_usage}

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

    def _parse_hourly_payload(self, payload) -> list:
        if not isinstance(payload, dict):
            return []

        candidates = []
        if isinstance(payload.get("hourlyMeterReads"), list):
            candidates = payload["hourlyMeterReads"]
        elif isinstance(payload.get("hourlyReads"), list):
            candidates = payload["hourlyReads"]
        else:
            data = payload.get("data") or {}
            hourly_block = data.get("HourlyUsage")
            if isinstance(hourly_block, list):
                candidates = hourly_block
            elif isinstance(hourly_block, dict):
                candidates = hourly_block.get("data") or []

        result = []
        for hour_usage in candidates:
            if not isinstance(hour_usage, dict):
                continue

            read_time = None
            if hour_usage.get("readTime"):
                read_time = self._parse_date(hour_usage["readTime"])
            elif hour_usage.get("date") and hour_usage.get("hour") is not None:
                day = self._parse_date(hour_usage["date"])
                if day:
                    read_time = day + timedelta(hours=int(hour_usage["hour"]))

            if read_time is None:
                continue

            kwh = hour_usage.get("kwhActual")
            if kwh is None:
                kwh = hour_usage.get("billedConsKwh")
            if kwh is None:
                kwh = hour_usage.get("kwh")

            cost = hour_usage.get("billingCharged")
            if cost is None:
                cost = hour_usage.get("billingCharge")
            if cost is None:
                cost = hour_usage.get("billedConsAmt")

            result.append(
                {
                    "hour": hour_usage.get("hour"),
                    "readTime": read_time,
                    "billingCharged": cost,
                    "kwhActual": kwh,
                    "reading": hour_usage.get("reading") or hour_usage.get("kwhRead"),
                }
            )

        return result

    @staticmethod
    def _parse_fpl_date(value) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            match = re.search(r"\/Date\((\d+)\)\/", value)
            if match:
                timestamp = int(match.group(1)) / 1000.0
                return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            parsed = FplNorthwestRegionApiClient._parse_date(value)
            if parsed:
                return parsed.strftime("%Y-%m-%d")
        return None

    @staticmethod
    def _parse_date(value) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
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
