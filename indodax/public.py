import urllib.parse
from typing import List
from .models import TickerResponse, PairInfo
from .private import PrivateAPI

class PublicAPI:
    BASE_URL_PUBLIC = "https://indodax.com"

    def get_ticker(self, pair: str) -> TickerResponse:
        if not pair.strip():
            raise ValueError("pair cannot be empty")
    
        endpoint = f"{self.PrivateAPI.BASE_URL_PRIVATE}/api/v2/ticker/price?symbol={urllib.parse.quote(pair.lower())}"
        resp = self.http.request("GET", endpoint)
        self._check_status(resp)
    
        data = resp.json()
        return TickerResponse(symbol=data["symbol"], price=data["price"])

    def get_pairs(self) -> List[PairInfo]:
        endpoint = f"{self.BASE_URL_PUBLIC}/api/pairs"
        resp = self.http.request("GET", endpoint)
        self._check_status(resp)
        
        results = []
        for p in resp.json():
            try:
                min_qty = float(p["trade_min_traded_currency"])
                if min_qty > 0:
                    results.append(PairInfo(id=p["id"].upper(), min_qty=min_qty))
            except (ValueError, KeyError):
                continue
        return results
