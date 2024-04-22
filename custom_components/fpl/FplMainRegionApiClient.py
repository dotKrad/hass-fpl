"""FPL Main region data collection api client"""

import json
import logging
from datetime import datetime, timedelta
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

URL_LOGIN = API_HOST + "/api/resources/login"

URL_BUDGET_BILLING_GRAPH = (
    API_HOST + "/api/resources/account/{account}/budgetBillingGraph"
)

URL_RESOURCES_PROJECTED_BILL = (
    API_HOST
    + "/api/resources/account/{account}/projectedBill"
    + "?premiseNumber={premise}&lastBilledDate={lastBillDate}"
)


URL_APPLIANCE_USAGE = (
    API_HOST + "/dashboard-api/resources/account/{account}/applianceUsage/{account}"
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
        URL = API_HOST + "/api/resources/header"
        async with async_timeout.timeout(TIMEOUT):
            response = await self.session.get(URL)

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

        URL_RESOURCES_ACCOUNT = API_HOST + "/api/resources/account/{account}"

        async with async_timeout.timeout(TIMEOUT):
            response = await self.session.get(
                URL_RESOURCES_ACCOUNT.format(account=account)
            )
        account_data = (await response.json())["data"]

        premise = account_data.get("premiseNumber").zfill(9)

        data["meterSerialNo"] = account_data["meterSerialNo"]
        #data["meterNo"] = account_data["meterNo"]
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
            return programName in programs and programs[programName]

        # Budget Billing program
        if hasProgram("BBL"):
            data["budget_bill"] = True
            bbl_data = await self.__getBBL_async(account, data)
            data.update(bbl_data)
        else:
            data["budget_bill"] = False

        # Get data from energy service
        data.update(
            await self.__getDataFromEnergyService(account, premise, currentBillDate, meterno)
        )

        # Get data from energy service ( hourly )
        # data.update(await self.__getDataFromEnergyServiceHourly(account, premise, meterno))

        data.update(await self.__getDataFromApplianceUsage(account, currentBillDate))
        data.update(await self.__getDataFromBalance(account))

        return data

    async def __getFromProjectedBill(self, account, premise, currentBillDate) -> dict:
        """get data from projected bill endpoint"""
        data = {}

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.get(
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

        except Exception as e:
            _LOGGER.error(e)

        return data

    async def __getBBL_async(self, account, projectedBillData) -> dict:
        """Get budget billing data"""
        _LOGGER.info("Getting budget billing data")
        data = {}

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.get(
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

            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.get(
                    URL_BUDGET_BILLING_GRAPH.format(account=account)
                )
                if response.status == 200:
                    r = (await response.json())["data"]
                    data["bill_to_date"] = float(r["eleAmt"])
                    data["defered_amount"] = float(r["defAmt"])
        except Exception as e:
            _LOGGER.error(e)

        return data

    async def __getDataFromEnergyService(
        self, account, premise, lastBilledDate, meterno
    ) -> dict:
        _LOGGER.info("Getting energy service data")

        date = str(lastBilledDate.strftime("%m%d%Y"))
        JSON = {
            "recordCount": 24,
            "status": 2,
            "channel": "WEB",
            "amrFlag": "Y",
            "accountType": "RESIDENTIAL",
            "revCode": "1",
            "premiseNumber": premise,
            "meterNo": meterno,
            "projectedBillFlag": True,
            "billComparisionFlag": True,
            "monthlyFlag": True,
            "frequencyType": "Daily",
            "lastBilledDate": date,
            "applicationPage": "resDashBoard",
        }
        URL_ENERGY_SERVICE = (
            API_HOST
            + "/dashboard-api/resources/account/{account}/energyService/{account}"
        )

        data = {}
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    URL_ENERGY_SERVICE.format(account=account), json=JSON
                )
                if response.status == 200:
                    rd = await response.json()
                    if "data" not in rd.keys():
                        return []

                    r = rd["data"]
                    dailyUsage = []

                    # totalPowerUsage = 0
                    if (
                        "data" in rd.keys()
                        and "DailyUsage" in rd["data"]
                        and "data" in rd["data"]["DailyUsage"]
                    ):
                        dailyData = rd["data"]["DailyUsage"]["data"]
                        for daily in dailyData:
                            if daily["missingDay"] != "true":
                                dailyUsage.append(
                                    {
                                        "usage": daily["kwhUsed"]
                                        if "kwhUsed" in daily.keys()
                                        else None,
                                        "cost": daily["billingCharge"]
                                        if "billingCharge" in daily.keys()
                                        else None,
                                        # "date": daily["date"],
                                        "max_temperature": daily[
                                            "averageHighTemperature"
                                        ]
                                        if "averageHighTemperature" in daily.keys()
                                        else None,
                                        "netDeliveredKwh": daily["netDeliveredKwh"]
                                        if "netDeliveredKwh" in daily.keys()
                                        else 0,
                                        "netReceivedKwh": daily["netReceivedKwh"]
                                        if "netReceivedKwh" in daily.keys()
                                        else 0,
                                        "netDeliveredReading": daily["netDeliveredReading"]
                                        if "netDeliveredReading" in daily.keys()
                                        else 0,
                                        "netReceivedReading": daily["netReceivedReading"]
                                        if "netReceivedReading" in daily.keys()
                                        else 0,
                                        "readTime": datetime.fromisoformat(
                                            daily[
                                                "readTime"
                                            ]  # 2022-02-25T00:00:00.000-05:00
                                        ),
                                    }
                                )
                            # totalPowerUsage += int(daily["kwhUsed"])

                        # data["total_power_usage"] = totalPowerUsage
                        data["daily_usage"] = dailyUsage

                    currentUsage = r["CurrentUsage"]
                    data["projectedKWH"] = currentUsage["projectedKWH"]
                    data["dailyAverageKWH"] = float(currentUsage["dailyAverageKWH"])
                    data["billToDateKWH"] = float(currentUsage["billToDateKWH"])
                    data["recMtrReading"] = int(currentUsage["recMtrReading"] or 0)
                    data["delMtrReading"] = int(currentUsage["delMtrReading"] or 0)
                    data["billStartDate"] = currentUsage["billStartDate"]
        except Exception as e:
            _LOGGER.error(e)

        return data

    async def __getDataFromEnergyServiceHourly(account, premise, meterno) -> dict:
        _LOGGER.info("Getting energy service hourly data")
    
        today = str(datetime.now().strftime("%m%d%Y"))
        JSON = {
            "status": 2,
            "channel": "WEB",
            "amrFlag": "Y",
            "accountType": "RESIDENTIAL",
            "revCode": "1",
            "premiseNumber": premise,
            "meterNo": meterno,
            "projectedBillFlag": False,
            "billComparisionFlag": False,
            "monthlyFlag": False,
            "frequencyType": "Hourly",
            "applicationPage": "resDashBoard",
            "startDate": today,
            "endDate":"",
        }
        
        URL_ENERGY_SERVICE = (
            API_HOST
            + "/dashboard-api/resources/account/{account}/energyService/{account}"
        )

        data = {}
        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    URL_ENERGY_SERVICE.format(account=account), json=JSON
                )
                if response.status == 200:
                    rd = await response.json()
                    if "data" not in rd.keys():
                        return []

                    r = rd["data"]
                    hourlyUsage = []

                    # totalPowerUsage = 0
                    if (
                        "data" in rd.keys()
                        and "HourlyUsage" in rd["data"]
                        and "data" in rd["data"]["HourlyUsage"]
                    ):
                        hourlyData = rd["data"]["HourlyUsage"]["data"]
                        for hourly in hourlyData:
                            hourlyUsage.append(
                                    {
                                        "usage": hourly["kwhUsed"]
                                        if "kwhUsed" in hourly.keys()
                                        else None,
                                        "cost": hourly["billingCharged"]
                                        if "billingCharged" in hourly.keys()
                                        else None,
                                        "temperature": hourly["temperature"]
                                        if "temperature" in hourly.keys()
                                        else None,
                                        "netDelivered": hourly["netDelivered"]
                                        if "netDelivered" in hourly.keys()
                                        else 0,
                                        "netReceived": hourly["netReceived"]
                                        if "netReceived" in hourly.keys()
                                        else 0,
                                        "reading": hourly["reading"]
                                        if "reading" in hourly.keys()
                                        else 0,
                                        "kwhActual": hourly["kwhActual"]
                                        if "kwhActual" in hourly.keys()
                                        else 0,
                                        "readTime": datetime.fromisoformat(
                                            hourly[
                                                "readTime"
                                            ]  # 2022-02-25T00:00:00.000-05:00
                                        ),
                                    }
                                )
                                
                        data["hourly_usage"] = hourlyUsage
        except Exception as e:
            _LOGGER.error(e)

        return data

    async def __getDataFromApplianceUsage(self, account, lastBilledDate) -> dict:
        """get data from appliance usage"""
        _LOGGER.info("Getting appliance usage data")

        JSON = {"startDate": str(lastBilledDate.strftime("%m%d%Y"))}
        data = {}

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.post(
                    URL_APPLIANCE_USAGE.format(account=account), json=JSON
                )
                if response.status == 200:
                    data = (await response.json())["data"]
                    if "electric" in data:
                        electric = data["electric"]

                        full = 100
                        for e in electric:
                            rr = round(float(e["percentageDollar"]))
                            if rr < full:
                                full = full - rr
                            else:
                                rr = full
                            data[e["category"].replace(" ", "_")] = rr
                    else:
                        _LOGGER.info("appliance usage data does not exist")
        except Exception as e:
            _LOGGER.error(e)

        return {"energy_percent_by_applicance": data}

    async def __getDataFromBalance(self, account) -> dict:
        """get data from appliance usage"""
        _LOGGER.info("Getting appliance usage data")

        data = {}

        URL_BALANCE = API_HOST + "/api/resources/account/{account}/balance?count=-1"

        try:
            async with async_timeout.timeout(TIMEOUT):
                response = await self.session.get(URL_BALANCE.format(account=account))
                if response.status == 200:
                    data = (await response.json())["data"]

                    indice = [i for i, x in enumerate(data) if x["details"] == "DEBT"][
                        0
                    ]

                    deb = data[indice]["amount"]

        except Exception as e:
            _LOGGER.error(e)

        return {"balance_data": data}
