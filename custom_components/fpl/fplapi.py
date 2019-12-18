import asyncio
import logging
import re
from datetime import timedelta, date

import aiohttp
import async_timeout
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 5


class FplApi(object):
    """A class for getting energy usage information from Florida Power & Light."""

    def __init__(self, username, password, is_tou, loop, session):
        """Initialize the data retrieval. Session should have BasicAuth flag set."""
        self._username = username
        self._password = password
        self._loop = loop
        self._session = session
        self._is_tou = is_tou
        self._account_number = None
        self._premise_number = None

        self.yesterday_kwh = None
        self.yesterday_dollars = None
        self.mtd_kwh = None
        self.mtd_dollars = None
        self.projected_bill = None

    async def login(self):
        """login and get account information"""
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get("https://www.fpl.com/api/resources/login",
                                               auth=aiohttp.BasicAuth(self._username, self._password))

        if (await response.json())["messages"][0]["messageCode"] != "login.success":
            raise Exception('login failure')

        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get("https://www.fpl.com/api/resources/header")
        json = await response.json()
        self._account_number = json["data"]["selectedAccount"]["data"]["accountNumber"]
        self._premise_number = json["data"]["selectedAccount"]["data"]["acctSecSettings"]["premiseNumber"]

    async def async_get_yesterday_usage(self):
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(self._build_daily_url())

        _LOGGER.debug("Response from API: %s", response.status)

        if response.status != 200:
            self.data = None
            return

        malformedXML = await response.read()

        cleanerXML = str(malformedXML).replace(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '', 1
        ).split("<ARG>@@", 1)[0]

        soup = BeautifulSoup(cleanerXML, 'html.parser')

        tool_text = soup.find("dataset", seriesname="$") \
            .find("set")["tooltext"]

        match = re.search(r"\{br\}kWh Usage: (.*?) kWh \{br\}", tool_text)
        if match:
            self.yesterday_kwh = match.group(1)

        match2 = re.search(r"\{br\}Approx\. Cost: (\$.*?) \{br\}", tool_text)
        if match2:
            self.yesterday_dollars = match2.group(1)

    async def async_get_mtd_usage(self):
        async with async_timeout.timeout(TIMEOUT, loop=self._loop):
            response = await self._session.get(
                "https://app.fpl.com/wps/myportal/EsfPortal")

        soup = BeautifulSoup(await response.text(), 'html.parser')

        self.mtd_kwh = soup.find(id="bpbsubcontainer") \
            .find("table", class_="bpbtab_style_bill", width=430) \
            .find_all("div", class_="bpbtabletxt")[-1].string

        self.mtd_dollars = soup \
            .find_all("div", class_="bpbusagebgnd")[1] \
            .find("div", class_="bpbusagedollartxt").getText().strip()

        self.projected_bill = soup.find(id="bpssmlsubcontainer") \
            .find("div", class_="bpsmonthbillbgnd") \
            .find("div", class_="bpsmnthbilldollartxt") \
            .getText().strip().replace("$", "")

    def _build_daily_url(self):
        end_date = date.today()
        start_date = end_date - timedelta(days=1)

        return ("https://app.fpl.com/wps/PA_ESFPortalWeb/getDailyConsumption"
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
