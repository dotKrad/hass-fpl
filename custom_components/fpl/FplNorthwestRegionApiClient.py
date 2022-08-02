"""FPL Northwest data collection api client"""
from datetime import datetime
import logging
import async_timeout
import boto3

from .const import TIMEOUT, API_HOST
from .aws_srp import AWSSRP
from .const import LOGIN_RESULT_OK

USER_POOL_ID = "us-east-1_w09KCowou"
CLIENT_ID = "4k78t7970hhdgtafurk158dr3a"

ACCOUNT_STATUS_ACTIVE = "ACT"

_LOGGER = logging.getLogger(__package__)


class FplNorthwestRegionApiClient:
    """FPL Northwest Api client"""

    def __init__(self, username, password, loop, session) -> None:
        self.session = session
        self.username = username
        self.password = password
        self.loop = loop
        self.id_token = None
        self.access_token = None
        self.refresh_token = None

    async def login(self):
        """login using aws"""
        client = await self.loop.run_in_executor(
            None, boto3.client, "cognito-idp", "us-east-1"
        )

        aws = AWSSRP(
            username=self.username,
            password=self.password,
            pool_id=USER_POOL_ID,
            client_id=CLIENT_ID,
            loop=self.loop,
            client=client,
        )
        tokens = await aws.authenticate_user()

        if "AccessToken" in tokens["AuthenticationResult"]:
            self.access_token = tokens["AuthenticationResult"]["AccessToken"]
            self.refresh_token = tokens["AuthenticationResult"]["RefreshToken"]
            self.id_token = tokens["AuthenticationResult"]["IdToken"]
            # Get User
            headers = {
                "Content-Type": "application/x-amz-json-1.1",
                "X-Amz-Target": "AWSCognitoIdentityProviderService.GetUser",
            }

            JSON = {"AccessToken": self.access_token}

            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    "https://cognito-idp.us-east-1.amazonaws.com/",
                    headers=headers,
                    json=JSON,
                )
            if response.status == 200:
                data = await response.json(content_type="application/x-amz-json-1.1")

            # InitiateAuth
            headers = {
                "Content-Type": "application/x-amz-json-1.1",
                "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
            }

            payload = {
                "AuthFlow": "REFRESH_TOKEN_AUTH",
                "AuthParameters": {
                    "DEVICE_KEY": None,
                    "REFRESH_TOKEN": self.refresh_token,
                },
                "ClientId": "4k78t7970hhdgtafurk158dr3a",
            }

            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    "https://cognito-idp.us-east-1.amazonaws.com/",
                    headers=headers,
                    json=payload,
                )
            if response.status == 200:
                data = await response.json(content_type="application/x-amz-json-1.1")

                self.access_token = data["AuthenticationResult"]["AccessToken"]
                self.id_token = tokens["AuthenticationResult"]["IdToken"]

            return LOGIN_RESULT_OK

    async def get_open_accounts(self):
        """
        Returns the open accounts
        """

        result = []
        URL = API_HOST + "/cs/gulf/ssp/v1/profile/accounts/list"

        headers = {"Authorization": f"Bearer {self.id_token}"}

        async with async_timeout.timeout(TIMEOUT):
            response = await self.session.get(URL, headers=headers)

        if response.status == 200:
            data = await response.json()

            for account in data["accounts"]:
                if account["accountStatus"] == ACCOUNT_STATUS_ACTIVE:
                    result.append(account["accountNumber"])

        return result

    async def logout(self):
        """log out from fpl"""

    async def update(self, account):
        """
        Returns the data collected from fpl
        """

        URL = (
            API_HOST
            + f"/cs/gulf/ssp/v1/accountservices/account/{account}/accountSummary?balance=y"
        )

        headers = {"Authorization": f"Bearer {self.id_token}"}
        async with async_timeout.timeout(TIMEOUT):
            response = await self.session.get(URL, headers=headers)

        result = {}

        if response.status == 200:
            data = await response.json()

            accountSumary = data["accountSummary"]["accountSummaryData"]
            billAndMetterInfo = accountSumary["billAndMeterInfo"]
            programInfo = accountSumary["programInfo"]

            result["budget_bill"] = False
            result["bill_to_date"] = billAndMetterInfo["asOfDateAmount"]

            result["projected_bill"] = billAndMetterInfo["projBillAmount"]
            result["projectedKWH"] = billAndMetterInfo["projBillKWH"]

            result["bill_to_date"] = billAndMetterInfo["asOfDateUsage"]
            result["billToDateKWH"] = billAndMetterInfo["asOfDateUsage"]

            result["daily_avg"] = billAndMetterInfo["dailyAvgAmount"]
            result["dailyAverageKWH"] = billAndMetterInfo["dailyAvgKwh"]

            result["billStartDate"] = programInfo["currentBillDate"]
            result["next_bill_date"] = programInfo["nextBillDate"]

            start = datetime.fromisoformat(result["billStartDate"])
            end = datetime.fromisoformat(result["next_bill_date"])
            today = datetime.fromisoformat(data["today"])

            result["service_days"] = (end - start).days
            result["as_of_days"] = (today - start).days

        return result
