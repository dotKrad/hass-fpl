"""Custom FPl api client"""
import logging
from datetime import datetime

import sys
import json
import aiohttp
import async_timeout

STATUS_CATEGORY_OPEN = "OPEN"
# Api login result
LOGIN_RESULT_OK = "OK"
LOGIN_RESULT_INVALIDUSER = "NOTVALIDUSER"
LOGIN_RESULT_INVALIDPASSWORD = "FAILEDPASSWORD"
LOGIN_RESULT_UNAUTHORIZED = "UNAUTHORIZED"
LOGIN_RESULT_FAILURE = "FAILURE"

_LOGGER = logging.getLogger(__package__)
TIMEOUT = 5

API_HOST = "https://www.fpl.com"

URL_LOGIN = API_HOST + "/api/resources/login"
URL_LOGOUT = API_HOST + "/api/resources/logout"
URL_RESOURCES_HEADER = API_HOST + "/api/resources/header"
URL_RESOURCES_ACCOUNT = API_HOST + "/api/resources/account/{account}"
URL_BUDGET_BILLING_GRAPH = (
    API_HOST + "/api/resources/account/{account}/budgetBillingGraph"
)

URL_RESOURCES_PROJECTED_BILL = (
    API_HOST
    + "/api/resources/account/{account}/projectedBill"
    + "?premiseNumber={premise}&lastBilledDate={lastBillDate}"
)

URL_ENERGY_SERVICE = (
    API_HOST + "/dashboard-api/resources/account/{account}/energyService/{account}"
)
URL_APPLIANCE_USAGE = (
    API_HOST + "/dashboard-api/resources/account/{account}/applianceUsage/{account}"
)
URL_BUDGET_BILLING_PREMISE_DETAILS = (
    API_HOST + "/api/resources/account/{account}/budgetBillingGraph/premiseDetails"
)


ENROLLED = "ENROLLED"
NOTENROLLED = "NOTENROLLED"


class FplApi:
    """A class for getting energy usage information from Florida Power & Light."""

    def __init__(self, username, password, session):
        """Initialize the data retrieval. Session should have BasicAuth flag set."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> dict:
        """Get data from fpl api"""
        data = {}
        data["accounts"] = []
        if await self.login() == LOGIN_RESULT_OK:
            accounts = await self.async_get_open_accounts()

            data["accounts"] = accounts
            for account in accounts:
                account_data = await self.__async_get_data(account)
                data[account] = account_data

            await self.logout()
        return data

    async def login(self):
        """login into fpl"""
        _LOGGER.info("Logging in")
        # login and get account information
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(
                    URL_LOGIN, auth=aiohttp.BasicAuth(self._username, self._password)
                )

            if response.status == 200:
                _LOGGER.info("Logging Successful")
                return LOGIN_RESULT_OK

            if response.status == 401:
                _LOGGER.error("Logging Unauthorized")
                json_data = json.loads(await response.text())

                if json_data["messageCode"] == LOGIN_RESULT_INVALIDUSER:
                    return LOGIN_RESULT_INVALIDUSER

                if json_data["messageCode"] == LOGIN_RESULT_INVALIDPASSWORD:
                    return LOGIN_RESULT_INVALIDPASSWORD

        except Exception as exception:
            _LOGGER.error("Error %s : %s", exception, sys.exc_info()[0])
            return LOGIN_RESULT_FAILURE

        return LOGIN_RESULT_FAILURE

    async def logout(self):
        """Logging out from fpl"""
        _LOGGER.info("Logging out")
        try:
            async with async_timeout.timeout(TIMEOUT):
                await self._session.get(URL_LOGOUT)
        except Exception:
            pass

    async def async_get_open_accounts(self):
        """Getting open accounts"""
        _LOGGER.info("Getting open accounts")
        result = []

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(URL_RESOURCES_HEADER)

            json_data = await response.json()
            accounts = json_data["data"]["accounts"]["data"]["data"]

            for account in accounts:
                if account["statusCategory"] == STATUS_CATEGORY_OPEN:
                    result.append(account["accountNumber"])

        except Exception:
            _LOGGER.error("Getting accounts %s", sys.exc_info())

        return result

    async def __async_get_data(self, account) -> dict:
        """Get data from resources endpoint"""
        _LOGGER.info("Getting Data")
        data = {}

        async with async_timeout.timeout(TIMEOUT):
            response = await self._session.get(
                URL_RESOURCES_ACCOUNT.format(account=account)
            )
        account_data = (await response.json())["data"]

        premise = account_data["premiseNumber"].zfill(9)

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

        # zip code
        # zip_code = accountData["serviceAddress"]["zip"]

        # projected bill
        pbData = await self.__getFromProjectedBill(account, premise, currentBillDate)
        data.update(pbData)

        # programs
        programsData = account_data["programs"]["data"]

        programs = dict()
        _LOGGER.info("Getting Programs")
        for program in programsData:
            if "enrollmentStatus" in program.keys():
                key = program["name"]
                programs[key] = program["enrollmentStatus"] == ENROLLED

        def hasProgram(programName) -> bool:
            return programName in programs.keys() and programs[programName]

        # Budget Billing program
        if hasProgram("BBL"):
            data["budget_bill"] = True
            bbl_data = await self.__getBBL_async(account, data)
            data.update(bbl_data)
        else:
            data["budget_bill"] = False

        data.update(
            await self.__getDataFromEnergyService(account, premise, currentBillDate)
        )

        data.update(await self.__getDataFromApplianceUsage(account, currentBillDate))
        return data

    async def __getFromProjectedBill(self, account, premise, currentBillDate) -> dict:
        """get data from projected bill endpoint"""
        data = {}

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(
                    URL_RESOURCES_PROJECTED_BILL.format(
                        account=account,
                        premise=premise,
                        lastBillDate=currentBillDate.strftime("%m%d%Y"),
                    )
                )

            if response.status == 200:

                projectedBillData = (await response.json())["data"]

                billToDate = float(projectedBillData["billToDate"])
                projectedBill = float(projectedBillData["projectedBill"])
                dailyAvg = float(projectedBillData["dailyAvg"])
                avgHighTemp = int(projectedBillData["avgHighTemp"])

                data["bill_to_date"] = billToDate
                data["projected_bill"] = projectedBill
                data["daily_avg"] = dailyAvg
                data["avg_high_temp"] = avgHighTemp

        except Exception:
            pass

        return data

    async def __getBBL_async(self, account, projectedBillData) -> dict:
        """Get budget billing data"""
        _LOGGER.info("Getting budget billing data")
        data = {}
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(
                    URL_BUDGET_BILLING_PREMISE_DETAILS.format(account=account)
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
        except Exception:
            pass

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(
                    URL_BUDGET_BILLING_GRAPH.format(account=account)
                )
                if response.status == 200:
                    r = (await response.json())["data"]
                    data["bill_to_date"] = float(r["eleAmt"])
                    data["defered_amount"] = float(r["defAmt"])
        except Exception:
            pass

        return data

    async def __getDataFromEnergyService(
        self, account, premise, lastBilledDate
    ) -> dict:
        _LOGGER.info("Getting data from energy service")

        date = str(lastBilledDate.strftime("%m%d%Y"))
        JSON = {
            "recordCount": 24,
            "status": 2,
            "channel": "WEB",
            "amrFlag": "Y",
            "accountType": "RESIDENTIAL",
            "revCode": "1",
            "premiseNumber": premise,
            "projectedBillFlag": True,
            "billComparisionFlag": True,
            "monthlyFlag": True,
            "frequencyType": "Daily",
            "lastBilledDate": date,
            "applicationPage": "resDashBoard",
        }

        data = {}

        async with async_timeout.timeout(TIMEOUT):
            response = await self._session.post(
                URL_ENERGY_SERVICE.format(account=account), json=JSON
            )
            if response.status == 200:
                r = (await response.json())["data"]
                dailyUsage = []

                # totalPowerUsage = 0
                if "data" in r["DailyUsage"]:
                    for daily in r["DailyUsage"]["data"]:
                        if (
                            "kwhUsed" in daily.keys()
                            and "billingCharge" in daily.keys()
                            and "date" in daily.keys()
                            and "averageHighTemperature" in daily.keys()
                        ):
                            dailyUsage.append(
                                {
                                    "usage": daily["kwhUsed"],
                                    "cost": daily["billingCharge"],
                                    # "date": daily["date"],
                                    "max_temperature": daily["averageHighTemperature"],
                                    "netDeliveredKwh": daily["netDeliveredKwh"]
                                    if "netDeliveredKwh" in daily.keys()
                                    else 0,
                                    "netReceivedKwh": daily["netReceivedKwh"]
                                    if "netReceivedKwh" in daily.keys()
                                    else 0,
                                    "readTime": daily["readTime"],
                                }
                            )
                            # totalPowerUsage += int(daily["kwhUsed"])

                    # data["total_power_usage"] = totalPowerUsage
                    data["daily_usage"] = dailyUsage

                data["projectedKWH"] = r["CurrentUsage"]["projectedKWH"]
                data["dailyAverageKWH"] = r["CurrentUsage"]["dailyAverageKWH"]
                data["billToDateKWH"] = r["CurrentUsage"]["billToDateKWH"]
                data["recMtrReading"] = r["CurrentUsage"]["recMtrReading"]
                data["delMtrReading"] = r["CurrentUsage"]["delMtrReading"]
                data["billStartDate"] = r["CurrentUsage"]["billStartDate"]
        return data

    async def __getDataFromApplianceUsage(self, account, lastBilledDate) -> dict:
        """get data from appliance usage"""
        _LOGGER.info("Getting data from appliance usage")

        JSON = {"startDate": str(lastBilledDate.strftime("%m%d%Y"))}
        data = {}
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.post(
                    URL_APPLIANCE_USAGE.format(account=account), json=JSON
                )
                if response.status == 200:
                    electric = (await response.json())["data"]["electric"]

                    full = 100
                    for e in electric:
                        rr = round(float(e["percentageDollar"]))
                        if rr < full:
                            full = full - rr
                        else:
                            rr = full
                        data[e["category"].replace(" ", "_")] = rr

        except Exception:
            pass

        return {"energy_percent_by_applicance": data}
