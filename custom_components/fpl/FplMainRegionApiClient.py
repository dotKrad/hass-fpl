"""FPL Main region data collection api client"""

import json
import logging
from datetime import datetime
import aiohttp
import async_timeout


from .const import (
    API_HOST,
    LOGIN_RESULT_FAILURE,
    LOGIN_RESULT_INVALIDPASSWORD,
    LOGIN_RESULT_INVALIDUSER,
    LOGIN_RESULT_OK,
    TIMEOUT,
)

STATUS_CATEGORY_OPEN = "OPEN"


def _parse_daily_read_time(read_time):
    if not read_time:
        return None
    if isinstance(read_time, datetime):
        return read_time
    try:
        return datetime.fromisoformat(read_time)
    except (TypeError, ValueError):
        return None


def _find_daily_usage_row(daily_usage):
    daily_rows = daily_usage.get("data") or []
    if not daily_rows:
        return None
    end_date = daily_usage.get("endDate")
    if end_date:
        for day_usage in daily_rows:
            if day_usage.get("date") == end_date:
                return day_usage
    return daily_rows[-1]


def _usage_block_ok(block):
    if not isinstance(block, dict):
        return False
    exception = block.get("exceptionDetails")
    if isinstance(exception, dict) and exception.get("requestStatus") == "Failed":
        return False
    return True


# URL_LOGIN = API_HOST + "/api/resources/login"
URL_LOGIN = (
    API_HOST
    + "/cs/customer/v1/registration/loginAndUseMigration?migrationToggle=Y&view=LoginMini"
)

URL_BUDGET_BILLING_GRAPH = (
    API_HOST + "/api/resources/account/{account}/budgetBillingGraph"
)

URL_RESOURCES_PROJECTED_BILL = (
    API_HOST
    + "/api/resources/account/{account}/projectedBill"
    + "?premiseNumber={premise}&lastBilledDate={lastBillDate}"
)


URL_BUDGET_BILLING_PREMISE_DETAILS = (
    API_HOST + "/api/resources/account/{account}/budgetBillingGraph/premiseDetails"
)


ENROLLED = "ENROLLED"
NOTENROLLED = "NOTENROLLED"

_LOGGER = logging.getLogger(__package__)


class FplMainRegionApiClient:
    """Fpl Main Region Api Client"""

    def __init__(self, username, password, loop, session) -> None:
        self.session = session
        self.username = username
        self.password = password
        self.loop = loop

    async def login(self):
        """login into fpl"""

        # login and get account information

        async with async_timeout.timeout(TIMEOUT):
            response = await self.session.get(
                URL_LOGIN,
                auth=aiohttp.BasicAuth(self.username, self.password),
            )

        if response.status == 200:
            # Get JWT token from headers if present
            jwt_token = response.headers.get("jwttoken")
            if jwt_token:
                self.jwt_token = jwt_token  # Store in a property
            return LOGIN_RESULT_OK

        if response.status == 401:
            json_data = json.loads(await response.text())

            if json_data["messageCode"] == LOGIN_RESULT_INVALIDUSER:
                return LOGIN_RESULT_INVALIDUSER

            if json_data["messageCode"] == LOGIN_RESULT_INVALIDPASSWORD:
                return LOGIN_RESULT_INVALIDPASSWORD

        return LOGIN_RESULT_FAILURE

    async def get_open_accounts(self):
        """
        Get open accounts

        Returns array with active account numbers
        """
        result = []
        URL = API_HOST + "/cs/customer/v1/resources/account"
        headers = {}
        if hasattr(self, "jwt_token") and self.jwt_token:
            headers["jwttoken"] = self.jwt_token

        start = 1
        page_size = 10

        while True:
            params = {"sortBy": "status", "count": str(page_size), "start": str(start)}
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.get(URL, headers=headers, params=params)

            json_data = await response.json()
            if response.status != 200:
                _LOGGER.warning(
                    "Account list request failed with status %s at start=%s",
                    response.status,
                    start,
                )
                break

            accounts_page = json_data.get("data", [])
            if not accounts_page:
                break

            for account in accounts_page:
                if account.get("statusCategory") == STATUS_CATEGORY_OPEN:
                    account_number = account.get("accountNumber")
                    if account_number:
                        result.append(account_number)

            if not json_data.get("hasMore"):
                break

            start += json_data.get("count", page_size)

        return result

    async def logout(self):
        """Logging out from fpl"""
        _LOGGER.info("Logging out")

        URL_LOGOUT = API_HOST + "/api/resources/logout"
        try:
            async with async_timeout.timeout(TIMEOUT):
                await self.session.get(URL_LOGOUT)
        except Exception as e:
            _LOGGER.error(e)

    async def update(self, account) -> dict:
        """Get data from resources endpoint"""
        data = {}
        URL_RESOURCES_ACCOUNT = (
            API_HOST
            + "/cs/customer/v1/accountservices/resources/account/{account}/select?view=account-lander"
        )
        try:
            headers = {}
            if hasattr(self, "jwt_token") and self.jwt_token:
                headers["jwttoken"] = self.jwt_token
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.get(
                    URL_RESOURCES_ACCOUNT.format(account=account), headers=headers
                )
            account_data = (await response.json()).get("data")
            if account_data:
                premise_number = account_data.get("premiseNumber")
                premise = None
                if premise_number:
                    premise = str(premise_number).zfill(9)
                    data["premise"] = premise

                if account_data.get("meterSerialNo") is not None:
                    data["meterSerialNo"] = account_data["meterSerialNo"]
                meterno = account_data.get("meterNo")

                current_bill_date_raw = account_data.get("currentBillDate")
                next_bill_date_raw = account_data.get("nextBillDate")
                if current_bill_date_raw and next_bill_date_raw:
                    currentBillDate = datetime.strptime(
                        current_bill_date_raw.replace("-", "").split("T")[0], "%Y%m%d"
                    ).date()

                    nextBillDate = datetime.strptime(
                        next_bill_date_raw.replace("-", "").split("T")[0], "%Y%m%d"
                    ).date()

                    data["current_bill_date"] = str(currentBillDate)
                    data["next_bill_date"] = str(nextBillDate)

                    today = datetime.now().date()

                    data["service_days"] = (nextBillDate - currentBillDate).days
                    data["as_of_days"] = (today - currentBillDate).days
                    data["remaining_days"] = (nextBillDate - today).days

                    programsData = account_data.get("programs", {}).get("data", [])

                    programs = dict()
                    _LOGGER.info("Getting Programs")
                    for program in programsData:
                        if "enrollmentStatus" in program.keys():
                            key = program["name"]
                            programs[key] = program["enrollmentStatus"] == ENROLLED

                    def hasProgram(programName) -> bool:
                        return programName in programs and programs[programName]

                    # Budget Billing program
                    if hasProgram("BBL"):
                        data["budget_bill"] = True
                        bbl_data = await self.__getBBL_async(account, data)
                        data.update(bbl_data)
                    else:
                        data["budget_bill"] = False

                    if premise and meterno:
                        energy_service_data = await self.get_energy_usage(
                            account, premise, currentBillDate, meterno
                        )
                        data.update(energy_service_data)

                        appliance_usage_data = await self.get_appliance_usage(
                            account, premise
                        )
                        data.update(appliance_usage_data)

        except Exception as e:
            _LOGGER.error("Failed to update account %s: %s", account, e, exc_info=True)

        data.update(await self.get_account_details(account))

        return data

    # async def __getFromProjectedBill(self, account, premise, currentBillDate) -> dict:
    #     """get data from projected bill endpoint"""
    #     data = {}

    #     try:
    #         headers = {}
    #         if hasattr(self, "jwt_token") and self.jwt_token:
    #             headers["jwttoken"] = self.jwt_token
    #         async with async_timeout.timeout(TIMEOUT):
    #             response = await self.session.get(
    #                 URL_RESOURCES_PROJECTED_BILL.format(
    #                     account=account,
    #                     premise=premise,
    #                     lastBillDate=currentBillDate.strftime("%m%d%Y"),
    #                 ),
    #                 headers=headers,
    #             )

    #         if response.status == 200:
    #             projectedBillData = (await response.json())["data"]

    #             # billToDate = float(projectedBillData["billToDate"])
    #             # projectedBill = float(projectedBillData["projectedBill"])
    #             # dailyAvg = float(projectedBillData["dailyAvg"])
    #             # avgHighTemp = int(projectedBillData["avgHighTemp"])

    #             # data["bill_to_date"] = billToDate
    #             # data["projected_bill"] = projectedBill
    #             # data["daily_avg"] = dailyAvg
    #             # data["avg_high_temp"] = avgHighTemp

    #     except Exception as e:
    #         _LOGGER.error(e)

    #     return data

    async def __getBBL_async(self, account, projectedBillData) -> dict:
        """Get budget billing data"""
        _LOGGER.info("Getting budget billing data")
        data = {}

        try:
            headers = {}
            if hasattr(self, "jwt_token") and self.jwt_token:
                headers["jwttoken"] = self.jwt_token
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.get(
                    URL_BUDGET_BILLING_PREMISE_DETAILS.format(account=account),
                    headers=headers,
                )
                if response.status == 200:
                    r = (await response.json())["data"]
                    dataList = r["graphData"]

                    # startIndex = len(dataList) - 1

                    billingCharge = 0
                    budgetBillDeferBalance = r["defAmt"]

                    projectedBill = projectedBillData["projected_bill"]
                    asOfDays = projectedBillData["as_of_days"]

                    for det in dataList:
                        billingCharge += det["actuallBillAmt"]

                    calc1 = (projectedBill + billingCharge) / 12
                    calc2 = (1 / 12) * (budgetBillDeferBalance)

                    projectedBudgetBill = round(calc1 + calc2, 2)
                    bbDailyAvg = round(projectedBudgetBill / 30, 2)
                    bbAsOfDateAmt = round(projectedBudgetBill / 30 * asOfDays, 2)

                    data["budget_billing_daily_avg"] = bbDailyAvg
                    data["budget_billing_bill_to_date"] = bbAsOfDateAmt

                    data["budget_billing_projected_bill"] = float(projectedBudgetBill)

            headers = {}
            if hasattr(self, "jwt_token") and self.jwt_token:
                headers["jwttoken"] = self.jwt_token
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.get(
                    URL_BUDGET_BILLING_GRAPH.format(account=account), headers=headers
                )
                if response.status == 200:
                    r = (await response.json())["data"]
                    data["bill_to_date"] = float(r["eleAmt"])
                    data["defered_amount"] = float(r["defAmt"])
        except Exception as e:
            _LOGGER.error(e)

        return data

    async def get_energy_usage(self, account, premise, lastBilledDate, meterno) -> dict:
        _LOGGER.info("Getting energy service data")

        # Tested using MITM proxy and iOS app.
        # This is the payload and url used by the iOS app.
        # iOS app: status "2" = active/open account, "4" = closed/inactive.
        json = {
            "status": "2",
            "accountType": "RESIDENTIAL",
            "premiseNumber": premise,
            # account select `currentBillDate` is sent as `lastBilledDate` (MMDDYYYY).
            "lastBilledDate": lastBilledDate.strftime("%m%d%Y"),
            "amrFlag": "Y",
            "revCode": "1",
            "meterNo": meterno,
        }
        URL_ENERGY_SERVICE = (
            API_HOST
            + "/cs/customer/v1/energydashboard/resources/energy-usage/account/{account}/mobile-energy-service"
        )

        data = {}
        try:
            headers = {}
            if hasattr(self, "jwt_token") and self.jwt_token:
                headers["jwttoken"] = self.jwt_token
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    URL_ENERGY_SERVICE.format(account=account),
                    json=json,
                    headers=headers,
                )
                if response.status == 200:
                    response_data = await response.json()
                    json_data = response_data.get("data") or {}

                    current_usage = json_data.get("CurrentUsage") or {}
                    if _usage_block_ok(current_usage):
                        if current_usage.get("projectedKWH") is not None:
                            data["projectedKWH"] = int(current_usage["projectedKWH"])
                        if current_usage.get("dailyAverageKWH") is not None:
                            data["dailyAverageKWH"] = float(
                                current_usage["dailyAverageKWH"]
                            )
                        if current_usage.get("billToDate") is not None:
                            data["billToDate"] = float(current_usage["billToDate"])
                        if current_usage.get("projectedBill") is not None:
                            data["projectedBill"] = float(
                                current_usage["projectedBill"]
                            )
                        if current_usage.get("dailyAvg") is not None:
                            data["dailyAvg"] = float(current_usage["dailyAvg"])
                        if current_usage.get("avgHighTemp") is not None:
                            data["avgHighTemp"] = int(current_usage["avgHighTemp"])
                        if current_usage.get("billToDateKWH") is not None:
                            data["billToDateKWH"] = float(
                                current_usage["billToDateKWH"]
                            )
                        data["recMtrReading"] = int(
                            current_usage.get("recMtrReading") or 0
                        )
                        data["delMtrReading"] = int(
                            current_usage.get("delMtrReading") or 0
                        )
                        if current_usage.get("billStartDate"):
                            data["billStartDate"] = datetime.strptime(
                                current_usage["billStartDate"], "%m-%d-%Y"
                            ).date()
                        if current_usage.get("billEndDate"):
                            data["billEndDate"] = datetime.strptime(
                                current_usage["billEndDate"], "%m-%d-%Y"
                            ).date()

                    daily_usage = json_data.get("DailyUsage") or {}
                    if _usage_block_ok(daily_usage):
                        day_usage = _find_daily_usage_row(daily_usage)
                        if day_usage:
                            read_time = _parse_daily_read_time(
                                day_usage.get("readTime")
                            )
                            if read_time is not None:
                                data["DailyUsage"] = {
                                    "kwhActual": float(day_usage.get("kwhActual") or 0),
                                    "billingCharge": float(
                                        day_usage.get("billingCharge") or 0
                                    ),
                                    "readTime": read_time,
                                    "reading": float(day_usage.get("reading") or 0),
                                    "netDeliveredKwh": float(
                                        day_usage.get("netDeliveredKwh") or 0
                                    ),
                                    "netDeliveredReading": float(
                                        day_usage.get("netDeliveredReading") or 0
                                    ),
                                }

        except Exception as e:
            _LOGGER.error(e)

        return data

    async def get_hourly_usage(self, account, premise, date) -> list:
        """get data from hourly usage for a specific date"""
        _LOGGER.info("Getting hourly usage data")

        URL_APPLIANCE_USAGE = (
            API_HOST
            + f"/cs/customer/v1/energydashboard/resources/energy-usage/account/{account}/mobile-hourly-usage"
        )

        JSON = {"premiseNumber": premise, "startDate": date.strftime("%m-%d-%Y")}

        data = []
        try:
            headers = {}
            if hasattr(self, "jwt_token") and self.jwt_token:
                headers["jwttoken"] = self.jwt_token
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    URL_APPLIANCE_USAGE,
                    json=JSON,
                    headers=headers,
                )
                if response.status == 200:
                    response_json = await response.json()
                    json_data = response_json.get("data") or {}
                    hourly_usage_block = json_data.get("HourlyUsage")
                    if isinstance(hourly_usage_block, list):
                        hourly_usage = hourly_usage_block
                    elif isinstance(hourly_usage_block, dict):
                        hourly_usage = hourly_usage_block.get("data") or []
                    else:
                        hourly_usage = []

                    for hour_usage in hourly_usage:
                        if not isinstance(hour_usage, dict):
                            continue
                        read_time_raw = hour_usage.get("readTime")
                        if read_time_raw is None:
                            continue
                        read_time = datetime.fromisoformat(read_time_raw)
                        data.append(
                            {
                                "hour": hour_usage.get(
                                    "hour"
                                ),  # 1 - 24 (Where 1 = from 12AM to 1AM)
                                "readTime": read_time,  # This is the end of the hour, for example 1AM.
                                "billingCharged": hour_usage.get("billingCharged"),
                                "kwhActual": hour_usage["kwhActual"],
                                "reading": hour_usage["reading"],
                            }
                        )
        except Exception as e:
            _LOGGER.error(e)

        return data

    async def get_appliance_usage(self, account, premise) -> dict:
        """get data from appliance usage"""
        _LOGGER.info("Getting appliance usage data")

        URL_APPLIANCE_USAGE = (
            API_HOST
            + "/cs/customer/v1/energyanalyzer/resources/{account}/getDisaggResp"
        )

        JSON = {"premiseId": premise, "accountNumber": account}
        data = {}

        try:
            headers = {}
            if hasattr(self, "jwt_token") and self.jwt_token:
                headers["jwttoken"] = self.jwt_token
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    URL_APPLIANCE_USAGE.format(account=account),
                    json=JSON,
                    headers=headers,
                )
                if response.status == 200:
                    response_json = await response.json()
                    json_data = response_json["data"]

                    bill_periods = json_data["billPeriods"]
                    if bill_periods:
                        for bill_period in bill_periods:
                            # We only care about the latest bill period.
                            # It appears that 1 is the latest, with 2 being two months ago, etc.
                            if int(bill_period["billPeriod"]) == 1:
                                data["appliance_usage"] = bill_period
                                break

        except Exception as e:
            _LOGGER.error(e)

        return data

    async def get_account_details(self, account_number: str) -> dict:
        """Get accounts"""

        data = {}

        ACCOUNTS_URL = (
            API_HOST
            + "/cs/customer/v1/accountservices/resources/loginNew?mediaChannel=IOS"
        )

        try:
            headers = {"Content-Type": "application/json"}
            if hasattr(self, "jwt_token") and self.jwt_token:
                headers["jwttoken"] = self.jwt_token
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    ACCOUNTS_URL, json={}, headers=headers
                )
                json_data = await response.json()
                if response.status == 200:
                    for account in json_data["data"]["AccountList"]["data"]:
                        if account["accountNumber"] != account_number:
                            continue

                        balances_drilldown = account.get("balancesDrilldown")
                        if balances_drilldown:
                            balances = balances_drilldown.get("data") or []
                            if balances:
                                amount = balances[0].get("amount")
                                if amount:
                                    data["balance"] = float(
                                        amount.replace("$", "").replace(",", "")
                                    )
                                due_date = balances[0].get("dueDate")
                                if due_date:
                                    try:
                                        data["balance_due_date"] = datetime.strptime(
                                            due_date, "%b %d, %Y"
                                        ).date()
                                    except ValueError:
                                        pass
                            break

                        actual_balance = account.get("actualBalance")
                        if actual_balance is not None:
                            data["balance"] = float(actual_balance)
                        elif account.get("balance") is not None:
                            data["balance"] = float(
                                str(account["balance"])
                                .replace("$", "")
                                .replace(",", "")
                            )

                        due_date_val = account.get("dueDateVal")
                        if due_date_val:
                            try:
                                data["balance_due_date"] = datetime.strptime(
                                    due_date_val, "%b %d, %Y"
                                ).date()
                            except ValueError:
                                pass
                        break

                return data

        except Exception as e:
            _LOGGER.error(
                "Failed to get account details for %s", account_number, exc_info=True
            )

        return data
