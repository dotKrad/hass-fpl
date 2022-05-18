import asyncio
import logging
import re
from datetime import timedelta, datetime, date as dt

import aiohttp
import async_timeout
import json
import sys


from bs4 import BeautifulSoup

STATUS_CATEGORY_OPEN = "OPEN"
# Api login result
LOGIN_RESULT_OK = "OK"
LOGIN_RESULT_INVALIDUSER = "NOTVALIDUSER"
LOGIN_RESULT_INVALIDPASSWORD = "FAILEDPASSWORD"
LOGIN_RESULT_UNAUTHORIZED = "UNAUTHORIZED"
LOGIN_RESULT_FAILURE = "FAILURE"

_LOGGER = logging.getLogger(__package__)
TIMEOUT = 30

URL_LOGIN = "https://www.fpl.com/api/resources/login"
URL_RESOURCES_HEADER = "https://www.fpl.com/api/resources/header"
URL_RESOURCES_ACCOUNT = "https://www.fpl.com/api/resources/account/{account}"
URL_RESOURCES_PROJECTED_BILL = "https://www.fpl.com/api/resources/account/{account}/projectedBill?premiseNumber={premise}&lastBilledDate={lastBillDate}"

ENROLLED = "ENROLLED"
NOTENROLLED = "NOTENROLLED"


class FplApi(object):
    """A class for getting energy usage information from Florida Power & Light."""

    def __init__(self, username, password, session):
        """Initialize the data retrieval. Session should have BasicAuth flag set."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> dict:
        # self._session = aiohttp.ClientSession()
        data = {}
        data["accounts"] = []
        if await self.login() == LOGIN_RESULT_OK:
            accounts = await self.async_get_open_accounts()

            data["accounts"] = accounts
            for account in accounts:
                accountData = await self.__async_get_data(account)
                data[account] = accountData

            await self.logout()
        return data

    async def login(self):
        _LOGGER.info("Logging in")
        """login and get account information"""
        result = LOGIN_RESULT_OK
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(
                    URL_LOGIN, auth=aiohttp.BasicAuth(self._username, self._password)
                )

            js = json.loads(await response.text())

            if response.reason == "Unauthorized":
                result = LOGIN_RESULT_UNAUTHORIZED

            if js["messages"][0]["messageCode"] != "login.success":
                _LOGGER.error(f"Logging Failure")
                result = LOGIN_RESULT_FAILURE

            _LOGGER.info(f"Logging Successful")

        except Exception as e:
            _LOGGER.error(f"Error {e} : {sys.exc_info()[0]}")
            result = LOGIN_RESULT_FAILURE

        return result

    async def logout(self):
        _LOGGER.info("Logging out")
        URL = "https://www.fpl.com/api/resources/logout"
        async with async_timeout.timeout(TIMEOUT):
            await self._session.get(URL)

    async def async_get_open_accounts(self):
        _LOGGER.info(f"Getting accounts")
        result = []

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(URL_RESOURCES_HEADER)

            js = await response.json()
            accounts = js["data"]["accounts"]["data"]["data"]

            for account in accounts:
                if account["statusCategory"] == STATUS_CATEGORY_OPEN:
                    result.append(account["accountNumber"])
        except Exception as e:
            _LOGGER.error(f"Getting accounts {e}")

        # self._account_number = js["data"]["selectedAccount"]["data"]["accountNumber"]
        # self._premise_number = js["data"]["selectedAccount"]["data"]["acctSecSettings"]["premiseNumber"]
        return result

    async def __async_get_data(self, account) -> dict:
        _LOGGER.info(f"Getting Data")
        data = {}

        async with async_timeout.timeout(TIMEOUT):
            response = await self._session.get(
                URL_RESOURCES_ACCOUNT.format(account=account)
            )
        accountData = (await response.json())["data"]

        premise = accountData["premiseNumber"].zfill(9)

        # currentBillDate
        currentBillDate = datetime.strptime(
            accountData["currentBillDate"].replace("-", "").split("T")[0], "%Y%m%d"
        ).date()

        # nextBillDate
        nextBillDate = datetime.strptime(
            accountData["nextBillDate"].replace("-", "").split("T")[0], "%Y%m%d"
        ).date()

        data["current_bill_date"] = str(currentBillDate)
        data["next_bill_date"] = str(nextBillDate)

        today = datetime.now().date()
        remaining = (nextBillDate - today).days
        days = (today - currentBillDate).days

        data["service_days"] = (nextBillDate - currentBillDate).days
        data["as_of_days"] = days
        data["remaining_days"] = remaining

        # zip code
        zip_code = accountData["serviceAddress"]["zip"]

        # projected bill
        pbData = await self.__getFromProjectedBill(account, premise, currentBillDate)
        data.update(pbData)

        # programs
        programsData = accountData["programs"]["data"]

        programs = dict()
        _LOGGER.info(f"Getting Programs")
        for program in programsData:
            if "enrollmentStatus" in program.keys():
                key = program["name"]
                programs[key] = program["enrollmentStatus"] == ENROLLED

        if programs["BBL"]:
            # budget billing
            data["budget_bill"] = True
            bblData = await self.__getBBL_async(account, data)
            data.update(bblData)

        data.update(
            await self.__getDataFromEnergyService(account, premise, currentBillDate)
        )

        data.update(await self.__getDataFromApplianceUsage(account, currentBillDate))
        return data

    async def __getFromProjectedBill(self, account, premise, currentBillDate) -> dict:
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
        except:
            pass

        return data

    async def __getBBL_async(self, account, projectedBillData) -> dict:
        _LOGGER.info(f"Getting budget billing data")
        data = {}

        URL = "https://www.fpl.com/api/resources/account/{account}/budgetBillingGraph/premiseDetails"
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(URL.format(account=account))
                if response.status == 200:
                    r = (await response.json())["data"]
                    dataList = r["graphData"]

                    startIndex = len(dataList) - 1

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
        except:
            pass

        URL = "https://www.fpl.com/api/resources/account/{account}/budgetBillingGraph"

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.get(URL.format(account=account))
                if response.status == 200:
                    r = (await response.json())["data"]
                    data["bill_to_date"] = float(r["eleAmt"])
                    data["defered_amount"] = float(r["defAmt"])
        except:
            pass

        return data

    async def __getDataFromEnergyService(
        self, account, premise, lastBilledDate
    ) -> dict:
        _LOGGER.info(f"Getting data from energy service")
        URL = "https://www.fpl.com/dashboard-api/resources/account/{account}/energyService/{account}"

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
            response = await self._session.post(URL.format(account=account), json=JSON)
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
                                    "usage": daily.get("kwhUsed"),
                                    "cost": daily.get("billingCharge"),
                                    "date": daily.get("date"),
                                    "max_temperature": daily.get(
                                        "averageHighTemperature"
                                    ),
                                    "netDeliveredKwh": daily.get("netDeliveredKwh"),
                                    "netReceivedKwh": daily.get("netReceivedKwh"),
                                    "readTime": daily.get("readTime"),
                                }
                            )
                            # totalPowerUsage += int(daily["kwhUsed"])

                    # data["total_power_usage"] = totalPowerUsage
                    data["daily_usage"] = dailyUsage

                data["projectedKWH"] = r["CurrentUsage"].get("projectedKWH")
                data["dailyAverageKWH"] = r["CurrentUsage"].get("dailyAverageKWH")
                data["billToDateKWH"] = r["CurrentUsage"].get("billToDateKWH")
                data["recMtrReading"] = r["CurrentUsage"].get("recMtrReading")
                data["delMtrReading"] = r["CurrentUsage"].get("delMtrReading")
                data["billStartDate"] = r["CurrentUsage"].get("billStartDate")
        return data

    async def __getDataFromApplianceUsage(self, account, lastBilledDate) -> dict:
        _LOGGER.info(f"Getting data from applicance usage")
        URL = "https://www.fpl.com/dashboard-api/resources/account/{account}/applianceUsage/{account}"
        JSON = {"startDate": str(lastBilledDate.strftime("%m%d%Y"))}
        data = {}
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self._session.post(
                    URL.format(account=account), json=JSON
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

        except:
            pass

        return {"energy_percent_by_applicance": data}
