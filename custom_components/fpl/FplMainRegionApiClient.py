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
        URL = API_HOST + "/cs/customer/v1/resources/header"
        headers = {}
        if hasattr(self, "jwt_token") and self.jwt_token:
            headers["jwttoken"] = self.jwt_token

        async with async_timeout.timeout(TIMEOUT):
            response = await self.session.get(URL, headers=headers)

        json_data = await response.json()
        accounts = json_data["data"]["accounts"]["data"]["data"]

        for account in accounts:
            if account["statusCategory"] == STATUS_CATEGORY_OPEN:
                result.append(account["accountNumber"])

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
        headers = {}
        if hasattr(self, "jwt_token") and self.jwt_token:
            headers["jwttoken"] = self.jwt_token
        async with async_timeout.timeout(TIMEOUT):
            response = await self.session.get(
                URL_RESOURCES_ACCOUNT.format(account=account), headers=headers
            )
        account_data = (await response.json())["data"]

        premise = account_data.get("premiseNumber").zfill(9)
        data["premise"] = premise

        data["meterSerialNo"] = account_data["meterSerialNo"]
        # data["meterNo"] = account_data["meterNo"]
        meterno = account_data["meterNo"]

        # currentBillDate
        currentBillDate = datetime.strptime(
            account_data["currentBillDate"].replace("-", "").split("T")[0], "%Y%m%d"
        ).date()

        # nextBillDate
        nextBillDate = datetime.strptime(
            account_data["nextBillDate"].replace("-", "").split("T")[0], "%Y%m%d"
        ).date()

        data["current_bill_date"] = str(currentBillDate)
        data["next_bill_date"] = str(nextBillDate)

        today = datetime.now().date()

        data["service_days"] = (nextBillDate - currentBillDate).days
        data["as_of_days"] = (today - currentBillDate).days
        data["remaining_days"] = (nextBillDate - today).days

        programsData = account_data["programs"]["data"]

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

        energy_service_data = await self.get_energy_usage(
            account, premise, currentBillDate, meterno
        )
        data.update(energy_service_data)

        appliance_usage_data = await self.get_appliance_usage(account, premise)
        data.update(appliance_usage_data)

        # Gets the account balance and past due status.
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
        json = {
            "status": "2",
            "accountType": "RESIDENTIAL",
            "premiseNumber": premise,
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
                    json_data = response_data["data"]

                    current_usage = json_data["CurrentUsage"]
                    data["projectedKWH"] = int(current_usage.get("projectedKWH"))
                    data["dailyAverageKWH"] = float(
                        current_usage.get("dailyAverageKWH")
                    )
                    data["billToDate"] = float(current_usage.get("billToDate"))
                    data["projectedBill"] = float(current_usage.get("projectedBill"))
                    data["dailyAvg"] = float(current_usage.get("dailyAvg"))
                    data["avgHighTemp"] = int(current_usage.get("avgHighTemp"))
                    data["billToDateKWH"] = float(current_usage.get("billToDateKWH"))
                    data["recMtrReading"] = int(current_usage.get("recMtrReading") or 0)
                    data["delMtrReading"] = int(current_usage.get("delMtrReading") or 0)
                    data["billStartDate"] = datetime.strptime(
                        current_usage.get("billStartDate"), "%m-%d-%Y"
                    ).date()
                    data["billEndDate"] = datetime.strptime(
                        current_usage.get("billEndDate"), "%m-%d-%Y"
                    ).date()

                    daily_usage = json_data["DailyUsage"]
                    last_day_usage = daily_usage["endDate"]

                    data["DailyUsage"] = {}
                    for day_usage in daily_usage["data"]:
                        # We want to get the last day's usage and use that as the sensor information.
                        # Given that this sensor should reset every day to the previous day's usage.
                        if day_usage["date"] == last_day_usage:
                            data["DailyUsage"]["kwhActual"] = float(
                                day_usage.get("kwhActual") or 0
                            )
                            data["DailyUsage"]["billingCharge"] = float(
                                day_usage.get("billingCharge") or 0
                            )
                            data["DailyUsage"]["readTime"] = datetime.fromisoformat(
                                day_usage.get("readTime")
                            )
                            data["DailyUsage"]["reading"] = float(
                                day_usage.get("reading")
                            )

                            # This is most likely not going to work, as this endpoint does not give any information related to delivery metrics.
                            # TODO: Figure out where the delivery metrics can be grabbed from.
                            data["DailyUsage"]["netDeliveredKwh"] = float(
                                day_usage.get("netDeliveredKwh") or 0
                            )
                            data["DailyUsage"]["netDeliveredReading"] = float(
                                day_usage.get("netDeliveredReading") or 0
                            )

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
                    json_data = response_json["data"]

                    hourly_usage = json_data["HourlyUsage"]["data"]

                    for hour_usage in hourly_usage:
                        read_time = datetime.fromisoformat(hour_usage["readTime"])
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
            _LOGGER.error(e)

        return data
