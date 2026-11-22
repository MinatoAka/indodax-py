import urllib.parse
from typing import List
from .models import TickerResponse, TickerData, PairInfo

class PublicAPI:
    BASE_URL_PUBLIC = "https://indodax.com"

    def get_ticker(self, pair: str) -> TickerResponse:
        if not pair.strip():
            raise ValueError("pair cannot be empty")
        
        endpoint = f"{self.BASE_URL_PUBLIC}/api/ticker/{urllib.parse.quote(pair.lower())}"
        resp = self.http.request("GET", endpoint)
        self._check_status(resp)
        
        data = resp.json()
        ticker_data = TickerData(**data["ticker"])
        return TickerResponse(ticker=ticker_data)

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