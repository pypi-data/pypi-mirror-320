import requests

try:
    import aiohttp
except ImportError:
    aiohttp = None

from datetime import datetime

from nbg_currency_api.exceptions import CurrencyAPIException
from nbg_currency_api.types import (
    CurrencyEnum,
    ClientModeEnum,
)
from nbg_currency_api.constants import BASE_URL


class CurrencyFetcherAPI:
    def __init__(
        self,
        date: datetime | None = None,
        currency: CurrencyEnum | None = None,
        mode: ClientModeEnum = ClientModeEnum.SYNC,
    ):
        self.date = date or datetime.now()
        self.currency = currency
        self.mode = mode
        if self.mode == ClientModeEnum.ASYNC and aiohttp is None:
            raise ImportError(
                "aiohttp is not installed. Install with 'pip install currency-rates[async]' to enable async mode."
            )

    def _build_url(self) -> str:
        formatted_date = self.date.strftime("%Y-%m-%d")
        if self.currency:
            return f"{BASE_URL}/en/json/?currencies={self.currency.value}&date={formatted_date}"
        return f"{BASE_URL}/en/json/?date={formatted_date}"

    def fetch(self) -> dict:
        url = self._build_url()
        response = requests.get(url)
        if not response.ok:
            raise CurrencyAPIException(
                f"Error fetching data: {response.status_code} {response.text}"
            )
        return response.json()

    async def afetch(self) -> dict:
        url = self._build_url()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise CurrencyAPIException(
                        f"Error fetching data: {response.status} {await response.text()}"
                    )
                return await response.json()
