import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@patch("nbg_currency_api.services.CurrencyFetcherAPI.afetch")
async def test_service_afetch(mock_afetch, service_async):
    mock_afetch.return_value = [
        {
            "date": "2025-01-12",
            "currencies": [
                {
                    "code": "USD",
                    "quantity": 1,
                    "rateFormated": "3.14",
                    "diffFormated": "0.01",
                    "rate": 3.14,
                    "name": "US Dollar",
                    "diff": 0.01,
                    "date": "2025-01-12",
                    "validFromDate": "2025-01-12",
                }
            ],
        }
    ]
    result = await service_async.afetch()

    assert result.date.isoformat() == "2025-01-12T00:00:00"
    assert len(result.currencies) == 1
    assert result.currencies[0].code == "USD"
