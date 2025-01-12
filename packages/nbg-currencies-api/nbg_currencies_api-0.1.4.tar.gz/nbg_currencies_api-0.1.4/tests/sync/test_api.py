import pytest
from unittest.mock import patch, MagicMock
from nbg_currency_api.constants import BASE_URL
from nbg_currency_api.exceptions import CurrencyAPIException


@patch("nbg_currency_api.api.requests.get")
def test_fetch_success(mock_get, currency_api_sync):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"rate": 3.14}
    mock_get.return_value = mock_response

    result = currency_api_sync.fetch()
    assert result == {"rate": 3.14}
    mock_get.assert_called_once_with(
        f"{BASE_URL}/en/json/?currencies=USD&date=2025-01-12"
    )


@patch("nbg_currency_api.api.requests.get")
def test_fetch_failure(mock_get, currency_api_sync):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_get.return_value = mock_response

    with pytest.raises(
        CurrencyAPIException, match="Error fetching data: 500 Internal Server Error"
    ):
        currency_api_sync.fetch()
