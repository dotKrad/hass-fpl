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


class FplApi(object):
    """A class for getting energy usage information from Florida Power & Light."""

    def __init__(self, username, password, loop, session):
        """Initialize the data retrieval. Session should have BasicAuth flag set."""
        self._username = username
        self._password = password
        self._loop = loop
        self._session = session

    async def async_get_mtd_usage(self):
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(
                "https://app.fpl.com/wps/myportal/EsfPortal"
            )

        soup = BeautifulSoup(await response.text(), "html.parser")

        self.mtd_kwh = (
            soup.find(id="bpbsubcontainer")
            .find("table", class_="bpbtab_style_bill", width=430)
            .find_all("div", class_="bpbtabletxt")[-1]
            .string
        )

        self.mtd_dollars = (
            soup.find_all("div", class_="bpbusagebgnd")[1]
            .find("div", class_="bpbusagedollartxt")
            .getText()
            .strip()
            .replace("$", "")
        )

        self.projected_bill = (
            soup.find(id="bpssmlsubcontainer")
            .find("div", class_="bpsmonthbillbgnd")
            .find("div", class_="bpsmnthbilldollartxt")
            .getText()
            .strip()
            .replace("$", "")
        )

        test = soup.find(
            class_="bpsusagesmlmnthtxt").getText().strip().split(" - ")
        self.start_period = test[0]
        self.end_period = test[1]



    async def login(self):
        """login and get account information"""
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(URL_LOGIN, auth=aiohttp.BasicAuth(self._username, self._password))

        js = json.loads(await response.text())

        if response.reason == "Unauthorized":
            return js["messageCode"]

        if js["messages"][0]["messageCode"] != "login.success":
            raise Exception("login failure")

        return LOGIN_RESULT_OK

    async def async_get_open_accounts(self):
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(URL_RESOURCES_HEADER)

        js = await response.json()
        accounts = js["data"]["accounts"]["data"]["data"]

        result = []

        for account in accounts:
            if account["statusCategory"] == STATUS_CATEGORY_OPEN:
                result.append(account["accountNumber"])
            # print(account["accountNumber"])
            # print(account["premiseNumber"])
            # print(account["statusCategory"])

        # self._account_number = js["data"]["selectedAccount"]["data"]["accountNumber"]
        # self._premise_number = js["data"]["selectedAccount"]["data"]["acctSecSettings"]["premiseNumber"]
        return result

    async def async_get_data(self, account):

        data = {}

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(URL_RESOURCES_ACCOUNT.format(account=account))
        accountData = (await response.json())["data"]

        premise = accountData["premiseNumber"].zfill(9)

        # currentBillDate
        currentBillDate = datetime.strptime(
            accountData["currentBillDate"].replace(
                "-", "").split("T")[0], "%Y%m%d"
        ).date()

        # nextBillDate
        nextBillDate = datetime.strptime(
            accountData["nextBillDate"].replace(
                "-", "").split("T")[0], "%Y%m%d"
        ).date()

        # zip code
        zip_code = accountData["serviceAddress"]["zip"]

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(URL_RESOURCES_PROJECTED_BILL.format(
                account=account,
                premise=premise,
                lastBillDate=currentBillDate.strftime("%m%d%Y")
            ))

        projectedBillData = (await response.json())["data"]

        serviceDays = int(projectedBillData["serviceDays"])
        billToDate = float(projectedBillData["billToDate"])
        projectedBill = float(projectedBillData["projectedBill"])
        asOfDays = int(projectedBillData["asOfDays"])
        dailyAvg = float(projectedBillData["dailyAvg"])
        avgHighTemp = int(projectedBillData["avgHighTemp"])

        url = (
            "https://app.fpl.com/wps/PA_ESFPortalWeb/getDailyConsumption"
            f"?premiseNumber={premise}"
            f"&startDate={currentBillDate.strftime('%Y%m%d')}"
            f"&endDate={dt.today().strftime('%Y%m%d')}"
            f"&accountNumber={account}"
            # "&accountType=ELE"
            f"&zipCode={zip_code}"
            "&consumption=0.0"
            "&usage=0.0"
            "&isMultiMeter=false"
            f"&lastAvailableDate={dt.today()}"
            # "&isAmiMeter=true"
            "&userType=EXT"
            # "&currentReading=64359"
            "&isResidential=true"
            # "&isTouUser=false"
            "&showGroupData=false"
            # "&isNetMeter=false"
            "&certifiedDate=1900/01/01"
            # "&acctNetMeter=false"
            "&tempType=max"
            "&viewType=dollar"
            "&ecDayHumType=NoHum"
            # "&ecHasMoveInRate=false"
            # "&ecMoveInRateVal="
            # "&lastAvailableIeeDate=20191230"
        )

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(url)

        if response.status != 200:
            self.data = None
            return

        malformedXML = await response.read()

        cleanerXML = (
            str(malformedXML)
            .replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "", 1)
            .split("<ARG>@@", 1)[0]
        )

        total_kw = 0
        total_cost = 0
        days = 0

        soup = BeautifulSoup(cleanerXML, "html.parser")
        items = soup.find("dataset", seriesname="$").find_all("set")

        details = []

        for item in items:
            # <set color="E99356" link="j-hourlyJs-001955543,2019/12/29T00:00:00,2019/12/29T00:00:00,8142998577,residential,null,20191206,20200108" tooltext="Day/Date: Dec. 29, 2019 {br}kWh Usage: 42 kWh {br}Approx. Cost: $4.42 {br}Daily High Temp:  \xc2\xb0F " value="4.42"></set>
            match = re.search(
                r"Date: (\w\w\w. \d\d, \d\d\d\d).*\{br\}kWh Usage: (.*?) kWh \{br\}.*Cost:\s\$([\w|.]+).*Temp:\s(\d+)",
                str(item),
            )
            if match:
                date = datetime.strptime(match.group(1), "%b. %d, %Y").date()
                usage = int(match.group(2))
                cost = float(match.group(3))
                max_temp = int(match.group(4))
                if usage == 0:
                    cost = 0

                total_kw += usage
                total_cost += cost
                days += 1

                day_detail = {}
                day_detail["date"] = str(date)
                day_detail["usage"] = usage
                day_detail["cost"] = cost
                day_detail["max_temperature"] = max_temp

                details.append(day_detail)

        remaining_days = serviceDays - asOfDays
        avg_kw = round(total_kw / days, 0)

        data["current_bill_date"] = str(currentBillDate)
        data["next_bill_date"] = str(nextBillDate)
        data["service_days"] = serviceDays
        data["bill_to_date"] = billToDate
        data["projected_bill"] = projectedBill
        data["as_of_days"] = asOfDays
        data["daily_avg"] = dailyAvg
        data["avg_high_temp"] = avgHighTemp
        data["remaining_days"] = remaining_days
        data["mtd_kwh"] = total_kw
        data["average_kwh"] = avg_kw

        return data
