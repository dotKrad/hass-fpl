"""Custom FPl api client"""
import sys
import json
import logging

import async_timeout


from .const import (
    CONF_ACCOUNTS,
    CONF_TERRITORY,
    FPL_MAINREGION,
    LOGIN_RESULT_FAILURE,
    LOGIN_RESULT_OK,
    TIMEOUT,
    API_HOST,
)

from .FplMainRegionApiClient import FplMainRegionApiClient
from .FplNorthwestRegionApiClient import FplNorthwestRegionApiClient


_LOGGER = logging.getLogger(__package__)


URL_TERRITORY = API_HOST + "/cs/customer/v1/territoryid/public/territory"


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
                return FPL_MAINREGION

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
        data[CONF_TERRITORY] = self._territory
        data[CONF_ACCOUNTS] = await self.apiClient.get_open_accounts()

        return data

    async def async_get_data(self) -> dict:
        """Get data from fpl api"""
        await self.initialize()
        data = {}
        data[CONF_ACCOUNTS] = []

        data[CONF_TERRITORY] = self._territory

        login_result = await self.apiClient.login()

        if login_result == LOGIN_RESULT_OK:
            accounts = await self.apiClient.get_open_accounts()

            data[CONF_ACCOUNTS] = accounts
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
