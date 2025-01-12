from dataclasses import dataclass
from typing import List
from datetime import datetime
from enum import Enum


@dataclass
class CurrencyRateItem:
    code: str
    quantity: int
    rateFormated: str
    diffFormated: str
    rate: float
    name: str
    diff: float
    date: datetime
    validFromDate: datetime


@dataclass
class CurrencyDataResponse:
    date: datetime
    currencies: List[CurrencyRateItem]


class ClientModeEnum(Enum):
    SYNC = "sync"
    ASYNC = "async"


class CurrencyEnum(Enum):
    AED = "AED"
    AMD = "AMD"
    AUD = "AUD"
    AZN = "AZN"
    BGN = "BGN"
    BRL = "BRL"
    BYN = "BYN"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"
    CZK = "CZK"
    DKK = "DKK"
    EGP = "EGP"
    EUR = "EUR"
    GBP = "GBP"
    HKD = "HKD"
    HUF = "HUF"
    ILS = "ILS"
    INR = "INR"
    IRR = "IRR"
    ISK = "ISK"
    JPY = "JPY"
    KGS = "KGS"
    KRW = "KRW"
    KWD = "KWD"
    KZT = "KZT"
    MDL = "MDL"
    NOK = "NOK"
    NZD = "NZD"
    PLN = "PLN"
    QAR = "QAR"
    RON = "RON"
    RSD = "RSD"
    RUB = "RUB"
    SEK = "SEK"
    SGD = "SGD"
    TJS = "TJS"
    TMT = "TMT"
    TRY = "TRY"
    UAH = "UAH"
    USD = "USD"
    UZS = "UZS"
    ZAR = "ZAR"
