import asyncio
import logging
import re
from datetime import timedelta, datetime, date as dt

import aiohttp
import async_timeout
import json


from bs4 import BeautifulSoup
from const import STATUS_CATEGORY_OPEN, LOGIN_RESULT_OK

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 5


class FplApi(object):
    """A class for getting energy usage information from Florida Power & Light."""

    def __init__(self, username, password, loop, session):
        """Initialize the data retrieval. Session should have BasicAuth flag set."""
        self._username = username
        self._password = password
        self._loop = loop
        self._session = session

    async def login(self):
        """login and get account information"""
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(
                "https://www.fpl.com/api/resources/login",
                auth=aiohttp.BasicAuth(self._username, self._password),
            )

        js = json.loads(await response.text())

        if response.reason == "Unauthorized":
            return js["messageCode"]

        if js["messages"][0]["messageCode"] != "login.success":
            raise Exception("login failure")

        return LOGIN_RESULT_OK

    async def async_get_open_accounts(self):
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(
                "https://www.fpl.com/api/resources/header"
            )
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
        # await self.async_get_yesterday_usage()
        # await self.async_get_mtd_usage()
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(
                "https://www.fpl.com/api/resources/account/" + account
            )
        data = (await response.json())["data"]

        premise = data["premiseNumber"].zfill(9)
        print(premise)

        # print(data["nextBillDate"].replace("-", "").split("T")[0])
        # print(data["currentBillDate"].replace("-", "").split("T")[0])

        start_date = datetime.strptime(
            data["currentBillDate"].replace("-", "").split("T")[0], "%Y%m%d").date()
        end_date = dt.today()

        last_day = datetime.strptime(
            data["nextBillDate"].replace("-", "").split("T")[0], "%Y%m%d").date()

        lasting_days = (last_day - dt.today()).days
        zip_code = data["serviceAddress"]["zip"]

        url = (
            "https://app.fpl.com/wps/PA_ESFPortalWeb/getDailyConsumption"
            f"?premiseNumber={premise}"
            f"&startDate={start_date.strftime('%Y%m%d')}"
            f"&endDate={end_date.strftime('%Y%m%d')}"
            f"&accountNumber={account}"
            # "&accountType=ELE"
            f"&zipCode={zip_code}"
            "&consumption=0.0"
            "&usage=0.0"
            "&isMultiMeter=false"
            f"&lastAvailableDate={end_date}"
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
                day_detail["date"] = date
                day_detail["usage"] = usage
                day_detail["cost"] = cost
                day_detail["max_temperature"] = max_temp

                details.append(day_detail)

                print(date)
                print(usage)
                print(cost)
                print(max_temp)

        print("TOTALS")
        print(total_kw)
        print(total_cost)

        print("Average")
        avg_cost = round(total_cost / days, 2)
        print(avg_cost)
        avg_kw = round(total_kw / days, 0)
        print(avg_kw)

        print("Projected")
        projected_cost = round(total_cost + avg_cost * lasting_days, 2)
        print(projected_cost)

        data = {}
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["service_days"] = (end_date - start_date).days
        data["current_days"] = days
        data["remaining_days"] = lasting_days
        data["details"] = details

        return data
        pass

    async def async_get_yesterday_usage(self):
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            url = self._build_daily_url()
            response = await self._session.get(url)

        _LOGGER.debug("Response from API: %s", response.status)

        if response.status != 200:
            self.data = None
            return

        malformedXML = await response.read()

        cleanerXML = (
            str(malformedXML)
            .replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "", 1)
            .split("<ARG>@@", 1)[0]
        )

        soup = BeautifulSoup(cleanerXML, "html.parser")

        tool_text = soup.find("dataset", seriesname="$").find("set")[
            "tooltext"]

        match = re.search(r"\{br\}kWh Usage: (.*?) kWh \{br\}", tool_text)
        if match:
            self.yesterday_kwh = match.group(1).replace("$", "")

        match2 = re.search(r"\{br\}Approx\. Cost: (\$.*?) \{br\}", tool_text)
        if match2:
            self.yesterday_dollars = match2.group(1).replace("$", "")

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

    def _build_daily_url(self):
        end_date = dt.today()
        start_date = end_date - timedelta(days=1)

        return (
            "https://app.fpl.com/wps/PA_ESFPortalWeb/getDailyConsumption"
            "?premiseNumber={premise_number}"
            "&accountNumber={account_number}"
            "&isTouUser={is_tou}"
            "&startDate={start_date}"
            "&endDate={end_date}"
            "&userType=EXT"
            "&isResidential=true"
            "&certifiedDate=2000/01/01"
            "&viewType=dollar"
            "&tempType=max"
            "&ecDayHumType=NoHum"
        ).format(
            premise_number=self._premise_number,
            account_number=self._account_number,
            is_tou=str(self._is_tou),
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )
