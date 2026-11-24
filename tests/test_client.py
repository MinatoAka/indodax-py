import pytest
import requests_mock
import hashlib
import hmac
import urllib.parse
from indodax import Client, IndodaxError
from indodax.crypto import build_query, sign_sha256

API_KEY = "test-api-key"
SECRET_KEY = "test-secret-key"

@pytest.fixture
def client():
    return Client(api_key=API_KEY, secret_key=SECRET_KEY)

def test_ticker_parsing(client):
    with requests_mock.Mocker() as m:
        mock_response = {
            "ticker": {
                "buy": "33569000",
                "sell": "33571000",
                "last": "33570000",
                "high": "34157000",
                "low": "32901000",
                "server_time": 1794876675
            }
        }
        m.get("https://indodax.com/api/ticker/ethidr", json=mock_response)

        res = client.get_ticker("ethidr")

        assert res.get_last_price() == 33570000.0
        assert res.get_highest_bid() == 33569000.0
        assert res.ticker.server_time == 1794876675

def test_balances_signing(client):
    expected_asset_raw = "0.00030391"

    def match_request(request, context):
        assert request.method == "GET"
        assert "/api/v2/account" in request.url

        parsed_url = urllib.parse.urlparse(request.url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        params = {k: v[0] for k, v in query_params.items()}
        canonical_query = build_query(params)
        expected_sig = hmac.new(SECRET_KEY.encode(), canonical_query.encode(), hashlib.sha256).hexdigest()

        assert request.headers["Sign"] == expected_sig
        assert request.headers["X-APIKEY"] == API_KEY

        context.status_code = 200
        return {
            "balances": [
                {"asset": "IDR", "free": "1500000"},
                {"asset": "ETH", "free": expected_asset_raw}
            ]
        }

    with requests_mock.Mocker() as m:
        m.get("https://api.indodax.com/api/v2/account", json=match_request)
        res = client.get_balances("ethidr")

        assert res.idr == 1500000.0
        assert res.asset_raw == expected_asset_raw

def test_submit_order_signing(client):
    expected_qty = "0.00030391"

    def match_request(request, context):
        assert request.method == "POST"
        assert request.url == "https://api.indodax.com/api/v2/order"

        body_str = request.text
        expected_sig = hmac.new(SECRET_KEY.encode(), body_str.encode(), hashlib.sha256).hexdigest()
        assert request.headers["Sign"] == expected_sig

        form_data = urllib.parse.parse_qs(body_str)
        assert form_data["quantity"][0] == expected_qty
        assert form_data["side"][0] == "SELL"
        assert form_data["type"][0] == "MARKET"

        context.status_code = 200
        return {
            "symbol": "ETHIDR",
            "orderId": 123456789,
            "side": "SELL",
            "type": "MARKET",
            "fullOrderId": "ethidr-market-123456789"
        }

    with requests_mock.Mocker() as m:
        m.post("https://api.indodax.com/api/v2/order", json=match_request)

        res = client.place_market_sell("ethidr", expected_qty)

        assert res.order_id == 123456789
        assert res.full_order_id == "ethidr-market-123456789"

def test_market_buy_rounds_down(client):
    def match_request(request, context):
        form_data = urllib.parse.parse_qs(request.text)
        assert form_data["quoteOrderQty"] == ["100000.99"]
        context.status_code = 200
        return {"symbol": "ETHIDR", "orderId": 123, "side": "BUY", "type": "MARKET"}

    with requests_mock.Mocker() as m:
        m.post("https://api.indodax.com/api/v2/order", json=match_request)
        client.place_market_buy("ethidr", "100000.999")

def test_market_buy_rejects_invalid_amount(client):
    with pytest.raises(ValueError):
        client.place_market_buy("ethidr", "0")
