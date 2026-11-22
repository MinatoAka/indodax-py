import time
from typing import List
from .crypto import build_query, sign_sha256
from .models import BalanceResult, SubmitOrderRequest, OrderResult, TradeHistoryRequest, Trade
from .exceptions import IndodaxError

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

    def get_balances(self, pair: str) -> BalanceResult:
        if not self.api_key or not self.secret_key:
            raise ValueError("missing credentials for private endpoint")
        
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
        pair_upper = pair.upper()
        base_asset = pair_upper.replace("IDR", "")
        
        res = BalanceResult(idr=0.0, asset=0.0, asset_raw="0")
        for b in data.get("balances", []):
            if b["asset"].upper() == "IDR":
                res.idr = float(b["free"])
            elif b["asset"].upper() == base_asset:
                res.asset_raw = b["free"]
                res.asset = float(b["free"])
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
        return OrderResult(**data)

    def place_market_buy(self, pair: str, idr_amount: float) -> OrderResult:
        return self.submit_order(SubmitOrderRequest(
            symbol=pair.upper(),
            side="BUY",
            quote_order_qty=f"{idr_amount:.2f}"
        ))

    def place_market_sell(self, pair: str, coin_amount_raw: str) -> OrderResult:
        return self.submit_order(SubmitOrderRequest(
            symbol=pair.upper(),
            side="SELL",
            quantity=coin_amount_raw
        ))

    def trade_history(self, req: TradeHistoryRequest) -> List[Trade]:
        if not self.api_key or not self.secret_key:
            raise ValueError("missing credentials for private endpoint")
        if not req.symbol:
            raise ValueError("symbol is mandatory for trade history")

        params = {
            "symbol": req.symbol.lower(),
            "timestamp": str(int(time.time() * 1000)),
            "recvWindow": "5000"
        }
        if req.order_id: params["orderId"] = req.order_id
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
        return [Trade(**t) for t in data]