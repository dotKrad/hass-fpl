"""Custom FPl api client"""
import sys
import json
import logging

from datetime import datetime, timedelta
import async_timeout


from .const import (
    LOGIN_RESULT_FAILURE,
    LOGIN_RESULT_OK,
    TIMEOUT,
    API_HOST,
)

from .FplMainRegionApiClient import FplMainRegionApiClient
from .FplNorthwestRegionApiClient import FplNorthwestRegionApiClient


_LOGGER = logging.getLogger(__package__)


URL_TERRITORY = API_HOST + "/cs/customer/v1/territoryid/public/territory"


FPL_MAINREGION = "FL01"
FPL_NORTHWEST = "FL02"


class NoTerrytoryAvailableException(Exception):
    """Thrown when not possible to determine user territory"""


class FplApi:
    """A class for getting energy usage information from Florida Power & Light."""

    def __init__(self, username, password, session, loop):
        """Initialize the data retrieval. Session should have BasicAuth flag set."""
        self._username = username
        self._password = password
        self._session = session
        self._loop = loop
        self._territory = None
        self.access_token = None
        self.id_token = None
        self.apiClient = None

    async def getTerritory(self):
        """get territory"""
        if self._territory is not None:
            return self._territory

        headers = {"userID": f"{self._username}", "channel": "WEB"}
        async with async_timeout.timeout(TIMEOUT):
            response = await self._session.get(URL_TERRITORY, headers=headers)

        if response.status == 200:
            json_data = json.loads(await response.text())

            territoryArray = json_data["data"]["territory"]
            if len(territoryArray) == 0:
                raise NoTerrytoryAvailableException()

            self._territory = territoryArray[0]
            return territoryArray[0]

    def isMainRegion(self):
        """Returns true if this account belongs to the main region, not northwest"""
        return self._territory == FPL_MAINREGION

    async def initialize(self):
        """initialize the api client"""
        self._territory = await self.getTerritory()

        # set the api client based on user's territory
        if self.apiClient is None:
            if self.isMainRegion():
                self.apiClient = FplMainRegionApiClient(
                    self._username, self._password, self._loop, self._session
                )
            else:
                self.apiClient = FplNorthwestRegionApiClient(
                    self._username, self._password, self._loop, self._session
                )

    async def get_basic_info(self):
        """returns basic info for sensor initialization"""
        await self.initialize()
        data = {}
        data["territory"] = self._territory
        data["accounts"] = await self.apiClient.get_open_accounts()

        return data

    async def async_get_data(self) -> dict:
        """Get data from fpl api"""
        await self.initialize()
        data = {
            "as_of_days": 5,
            "avg_high_temp": 89,
            "billStartDate": "07-27-2022",
            "billToDateKWH": "196",
            "bill_to_date": 160.1,
            "budget_bill": True,
            "budget_billing_bill_to_date": 18.61,
            "budget_billing_daily_avg": 3.72,
            "budget_billing_projected_bill": 111.69,
            "current_bill_date": "2022-07-27",
            "dailyAverageKWH": 39,
            "daily_avg": 5.25,
            "daily_usage": [],
            "defered_amount": -6.84,
            "delMtrReading": "15929",
            "energy_percent_by_applicance": {},
            "meterSerialNo": "20948426",
            "next_bill_date": "2022-08-26",
            "projectedKWH": "1176",
            "projected_bill": 163.77,
            "recMtrReading": "",
            "remaining_days": 25,
            "service_days": 30,
        }
        data["accounts"] = []

        data["territory"] = self._territory

        print(self._territory)

        login_result = await self.apiClient.login()

        if login_result == LOGIN_RESULT_OK:
            accounts = await self.apiClient.get_open_accounts()

            data["accounts"] = accounts
            for account in accounts:
                data[account] = await self.apiClient.update(account)

            await self.apiClient.logout()
        return data

    async def login(self):
        """method to use in config flow"""
        try:
            await self.initialize()

            _LOGGER.info("Logging in")
            # login and get account information

            return await self.apiClient.login()

        except Exception as exception:
            _LOGGER.error("Error %s : %s", exception, sys.exc_info()[0])
            return LOGIN_RESULT_FAILURE

    async def async_get_open_accounts(self):
        """return open accounts"""
        self.initialize()
        return await self.apiClient.get_open_accounts()

    async def logout(self):
        """log out from fpl"""
        return await self.apiClient.logout()
