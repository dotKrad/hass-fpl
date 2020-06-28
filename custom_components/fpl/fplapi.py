import asyncio
import logging
import re
from datetime import timedelta, datetime, date as dt

import aiohttp
import async_timeout
import json


from bs4 import BeautifulSoup
from .const import STATUS_CATEGORY_OPEN, LOGIN_RESULT_OK

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 5

URL_LOGIN = "https://www.fpl.com/api/resources/login"
URL_RESOURCES_HEADER = "https://www.fpl.com/api/resources/header"
URL_RESOURCES_ACCOUNT = "https://www.fpl.com/api/resources/account/{account}"
URL_RESOURCES_PROJECTED_BILL = "https://www.fpl.com/api/resources/account/{account}/projectedBill?premiseNumber={premise}&lastBilledDate={lastBillDate}"

ENROLLED = "ENROLLED"
NOTENROLLED = "NOTENROLLED"


class FplApi(object):
    """A class for getting energy usage information from Florida Power & Light."""

    def __init__(self, username, password, loop, session):
        """Initialize the data retrieval. Session should have BasicAuth flag set."""
        self._username = username
        self._password = password
        self._loop = loop
        self._session = session

    async def login(self):
        _LOGGER.info("Logging")
        """login and get account information"""
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(
                URL_LOGIN, auth=aiohttp.BasicAuth(self._username, self._password)
            )

        js = json.loads(await response.text())

        if response.reason == "Unauthorized":
            raise Exception(js["messageCode"])

        if js["messages"][0]["messageCode"] != "login.success":
            _LOGGER.error(f"Logging Failure")
            raise Exception("login failure")

        _LOGGER.info(f"Logging Successful")
        return LOGIN_RESULT_OK

    async def async_get_open_accounts(self):
        _LOGGER.info(f"Getting accounts")
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(URL_RESOURCES_HEADER)

        js = await response.json()
        accounts = js["data"]["accounts"]["data"]["data"]

        result = []

        for account in accounts:
            if account["statusCategory"] == STATUS_CATEGORY_OPEN:
                result.append(account["accountNumber"])

        # self._account_number = js["data"]["selectedAccount"]["data"]["accountNumber"]
        # self._premise_number = js["data"]["selectedAccount"]["data"]["acctSecSettings"]["premiseNumber"]
        return result

    async def async_get_data(self, account):
        _LOGGER.info(f"Getting Data")
        data = {}

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
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
        pbData = await self.getFromProjectedBill(account, premise, currentBillDate)
        data.update(pbData)

        # programs
        programsData = accountData["programs"]["data"]

        programs = dict()
        _LOGGER.info(f"Getting Programs")
        for program in programsData:
            if "enrollmentStatus" in program.keys():
                key = program["name"]
                _LOGGER.info(f"{key} : {program['enrollmentStatus']}")
                programs[key] = program["enrollmentStatus"] == ENROLLED

        if programs["BBL"]:
            # budget billing
            data["budget_bill"] = True
            bblData = await self.getBBL_async(account)
            data.update(bblData)

        data.update(
            await self.getDataFromEnergyService(account, premise, currentBillDate)
        )

        data.update(await self.getDataFromApplianceUsage(account, currentBillDate))
        return data

    async def getFromProjectedBill(self, account, premise, currentBillDate):
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(
                URL_RESOURCES_PROJECTED_BILL.format(
                    account=account,
                    premise=premise,
                    lastBillDate=currentBillDate.strftime("%m%d%Y"),
                )
            )

        if response.status == 200:
            data = {}
            projectedBillData = (await response.json())["data"]

            billToDate = float(projectedBillData["billToDate"])
            projectedBill = float(projectedBillData["projectedBill"])
            dailyAvg = float(projectedBillData["dailyAvg"])
            avgHighTemp = int(projectedBillData["avgHighTemp"])

            data["bill_to_date"] = billToDate
            data["projected_bill"] = projectedBill
            data["daily_avg"] = dailyAvg
            data["avg_high_temp"] = avgHighTemp
            return data

        return []

    async def getBBL_async(self, account):
        URL = "https://www.fpl.com/api/resources/account/{account}/budgetBillingGraph"

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(URL.format(account=account))
            if response.status == 200:
                r = (await response.json())["data"]
                data = {}
                data["projected_budget_bill"] = float(r["bbAmt"])
                data["bill_to_date"] = float(r["eleAmt"])
                data["defered_amount"] = float(r["defAmt"])
                return data

        return []

    async def getDataFromEnergyService(self, account, premise, lastBilledDate):
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
            "meterNo": "D3117",
            "projectedBillFlag": True,
            "billComparisionFlag": True,
            "monthlyFlag": True,
            "frequencyType": "Daily",
            "lastBilledDate": date,
            "applicationPage": "resDashBoard",
        }

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.post(URL.format(account=account), json=JSON)
            if response.status == 200:
                r = (await response.json())["data"]
                dailyUsage = []

                for daily in r["DailyUsage"]["data"]:
                    dailyUsage.append(
                        {
                            "usage": daily["kwhUsed"],
                            "cost": daily["billingCharge"],
                            "date": daily["date"],
                            "max_temperature": daily["averageHighTemperature"],
                        }
                    )

                return {"daily_usage": dailyUsage}

        return []

    async def getDataFromApplianceUsage(self, account, lastBilledDate):
        URL = "https://www.fpl.com/dashboard-api/resources/account/{account}/applianceUsage/{account}"
        JSON = {"startDate": str(lastBilledDate.strftime("%m%d%Y"))}

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.post(URL.format(account=account), json=JSON)
            if response.status == 200:
                electric = (await response.json())["data"]["electric"]
                data = {}
                full = 100
                for e in electric:
                    rr = round(float(e["percentageDollar"]))
                    if rr < full:
                        full = full - rr
                    else:
                        rr = full
                    data[e["category"].replace(" ", "_")] = rr

                return {"energy_percent_by_applicance": data}

        return []
