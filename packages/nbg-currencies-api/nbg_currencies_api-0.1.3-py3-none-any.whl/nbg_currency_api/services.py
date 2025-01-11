from datetime import datetime

from nbg_currency_api.api import CurrencyFetcherAPI
from nbg_currency_api.types import (
    ClientModeEnum,
    CurrencyDataResponse,
    CurrencyRateItem,
    CurrencyEnum,
)


class NBGCurrencyService:
    def __init__(
        self,
        date: datetime | None = None,
        currency: CurrencyEnum | None = None,
        mode: ClientModeEnum = ClientModeEnum.SYNC,
    ):
        self.date = date or datetime.now()
        self.currency = currency
        self.mode = mode
        self.api = CurrencyFetcherAPI(self.date, self.currency, self.mode)

    @staticmethod
    def _normalize_data(data: dict) -> CurrencyDataResponse:
        first_item = data[0]
        return CurrencyDataResponse(
            date=datetime.fromisoformat(first_item["date"]),
            currencies=[
                CurrencyRateItem(
                    code=currency["code"],
                    quantity=currency["quantity"],
                    rateFormated=currency["rateFormated"],
                    diffFormated=currency["diffFormated"],
                    rate=currency["rate"],
                    name=currency["name"],
                    diff=currency["diff"],
                    date=datetime.fromisoformat(currency["date"]),
                    validFromDate=datetime.fromisoformat(currency["validFromDate"]),
                )
                for currency in first_item["currencies"]
            ],
        )

    def fetch(self) -> CurrencyDataResponse:
        raw_data = self.api.fetch()
        return self._normalize_data(raw_data)

    async def afetch(self) -> CurrencyDataResponse:
        raw_data = await self.api.afetch()
        return self._normalize_data(raw_data)
