import pytest
from datetime import datetime

from nbg_currency_api.types import CurrencyEnum, ClientModeEnum
from nbg_currency_api.services import NBGCurrencyService
from nbg_currency_api.api import CurrencyFetcherAPI


@pytest.fixture
def service_sync():
    return NBGCurrencyService(
        date=datetime(2025, 1, 12),
        currency=CurrencyEnum.USD,
        mode=ClientModeEnum.SYNC,
    )


@pytest.fixture
def currency_api_sync():
    return CurrencyFetcherAPI(
        date=datetime(2025, 1, 12),
        currency=CurrencyEnum.USD,
        mode=ClientModeEnum.SYNC,
    )


@pytest.fixture
def currency_api_async():
    return CurrencyFetcherAPI(
        date=datetime(2025, 1, 12),
        currency=CurrencyEnum.USD,
        mode=ClientModeEnum.ASYNC,
        delay=0.1,
        retries=10,
    )


@pytest.fixture
def service_async():
    return NBGCurrencyService(
        date=datetime(2025, 1, 12),
        currency=CurrencyEnum.USD,
        mode=ClientModeEnum.ASYNC,
    )
