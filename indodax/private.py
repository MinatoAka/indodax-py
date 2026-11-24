from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import List
import time

from .crypto import build_query, sign_sha256
from .models import BalanceResult, SubmitOrderRequest, OrderResult, TradeHistoryRequest, Trade


class PrivateAPI:
    BASE_URL_PRIVATE = "https://api.indodax.com"

    def _get_private_headers(self, signature: str, is_post: bool = False) -> dict:
        headers = {
            "Accept": "application/json",
            "X-APIKEY": self.api_key,
            "Sign": signature
        }
        if is_post:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        return headers

    @staticmethod
    def _normalize_pair(pair: str) -> str:
        if not isinstance(pair, str) or not pair.strip():
            raise ValueError("pair cannot be empty")

        pair_upper = pair.strip().upper()
        if not pair_upper.endswith("IDR") or len(pair_upper) <= 3:
            raise ValueError("pair must be an IDR market, for example ethidr")
        return pair_upper

    def get_balances(self, pair: str) -> BalanceResult:
        if not self.api_key or not self.secret_key:
            raise ValueError("missing credentials for private endpoint")

        pair_upper = self._normalize_pair(pair)
        base_asset = pair_upper[:-3]

        params = {
            "timestamp": str(int(time.time() * 1000)),
            "recvWindow": "5000"
        }
        query = build_query(params)
        sig = sign_sha256(query, self.secret_key)

        endpoint = f"{self.BASE_URL_PRIVATE}/api/v2/account?{query}"
        resp = self.http.request("GET", endpoint, headers=self._get_private_headers(sig))
        self._check_status(resp)

        data = resp.json()
        res = BalanceResult(idr=0.0, asset=0.0, asset_raw="0")
        idr_found = False
        asset_found = False

        for b in data.get("balances", []):
            asset = b.get("asset", "").upper()
            free = b.get("free")
            if free is None:
                continue

            if asset == "IDR":
                res.idr = float(free)
                idr_found = True
            elif asset == base_asset:
                res.asset_raw = str(free)
                res.asset = float(free)
                asset_found = True

        if not idr_found:
            raise ValueError("IDR balance was not found in the API response")
        if not asset_found:
            raise ValueError(f"{base_asset} balance was not found in the API response")
        return res

    def submit_order(self, req: SubmitOrderRequest) -> OrderResult:
        if not self.api_key or not self.secret_key:
            raise ValueError("missing credentials for private endpoint")

        params = {
            "symbol": req.symbol,
            "side": req.side.upper(),
            "type": "MARKET",
            "timestamp": str(int(time.time() * 1000)),
            "recvWindow": "5000"
        }
        if req.quantity:
            params["quantity"] = req.quantity
        if req.quote_order_qty:
            params["quoteOrderQty"] = req.quote_order_qty

        payload = build_query(params)
        sig = sign_sha256(payload, self.secret_key)

        endpoint = f"{self.BASE_URL_PRIVATE}/api/v2/order"
        resp = self.http.request("POST", endpoint, headers=self._get_private_headers(sig, is_post=True), data=payload)
        self._check_status(resp)

        data = resp.json()
        return OrderResult(
            symbol=data.get("symbol", ""),
            order_id=data.get("orderId", 0),
            client_order_id=data.get("clientOrderId"),
            side=data.get("side"),
            type=data.get("type"),
            full_order_id=data.get("fullOrderId")
        )

    def place_market_buy(self, pair: str, idr_amount) -> OrderResult:
        pair_upper = self._normalize_pair(pair)
        try:
            amount = Decimal(str(idr_amount))
        except (InvalidOperation, ValueError):
            raise ValueError("idr_amount must be a finite decimal amount")

        if not amount.is_finite() or amount <= 0:
            raise ValueError("idr_amount must be a positive finite amount")

        # Harus IDR bulat
        if amount != amount.to_integral_value():
            raise ValueError("quoteOrderQty must be a whole IDR amount")

        return self.submit_order(SubmitOrderRequest(
            symbol=pair_upper,
            side="BUY",
            quote_order_qty=str(int(amount))
        ))

    def place_market_sell(self, pair: str, coin_amount_raw: str) -> OrderResult:
        pair_upper = self._normalize_pair(pair)
        return self.submit_order(SubmitOrderRequest(
            symbol=pair_upper,
            side="SELL",
            quantity=coin_amount_raw
        ))

    def trade_history(self, req: TradeHistoryRequest) -> List[Trade]:
        if not self.api_key or not self.secret_key:
            raise ValueError("missing credentials for private endpoint")
        if not req.symbol:
            raise ValueError("symbol is mandatory for trade history")

        symbol = self._normalize_pair(req.symbol)
        params = {
            "symbol": symbol.lower(),
            "timestamp": str(int(time.time() * 1000)),
            "recvWindow": "5000"
        }
        if req.full_order_id: params["orderId"] = req.full_order_id
        if req.client_order_id: params["clientOrderId"] = req.client_order_id
        if req.start_time > 0: params["startTime"] = str(req.start_time)
        if req.end_time > 0: params["endTime"] = str(req.end_time)
        if req.limit > 0: params["limit"] = str(req.limit)
        if req.sort: params["sort"] = req.sort

        query = build_query(params)
        sig = sign_sha256(query, self.secret_key)

        endpoint = f"{self.BASE_URL_PRIVATE}/api/v2/myTrades?{query}"
        resp = self.http.request("GET", endpoint, headers=self._get_private_headers(sig))
        self._check_status(resp)

        data = resp.json().get("data", [])
        trades = []
        for t in data:
            trades.append(Trade(
                trade_id=t.get("tradeId", ""),
                order_id=t.get("orderId", ""),
                client_order_id=t.get("clientOrderId", ""),
                symbol=t.get("symbol", ""),
                price=t.get("price", "0"),
                qty=t.get("qty", "0"),
                quote_qty=t.get("quoteQty", "0"),
                commission=t.get("commission", "0"),
                commission_asset=t.get("commissionAsset", ""),
                is_buyer=t.get("isBuyer", False),
                is_maker=t.get("isMaker", False),
                time=t.get("time", 0)
            ))
        return trades
