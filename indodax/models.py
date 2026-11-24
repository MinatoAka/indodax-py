from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BalanceResult:
    idr: float
    asset: float
    asset_raw: str

@dataclass
class SubmitOrderRequest:
    symbol: str
    side: str
    quote_order_qty: Optional[str] = None
    quantity: Optional[str] = None

@dataclass
class OrderResult:
    symbol: str
    order_id: int
    client_order_id: Optional[str] = None
    side: Optional[str] = None
    type: Optional[str] = None
    full_order_id: Optional[str] = None

@dataclass
class PairInfo:
    id: str
    min_qty: float

@dataclass
class TickerData:
    buy: str
    sell: str
    last: str
    high: str
    low: str
    server_time: int

@dataclass
class TickerResponse:
    ticker: TickerData

    def get_last_price(self) -> float: return float(self.ticker.last)
    def get_highest_bid(self) -> float: return float(self.ticker.buy)
    def get_lowest_ask(self) -> float: return float(self.ticker.sell)
    def get_day_high(self) -> float: return float(self.ticker.high)
    def get_day_low(self) -> float: return float(self.ticker.low)

@dataclass
class TradeHistoryRequest:
    symbol: str
    full_order_id: str = ""
    client_order_id: str = ""
    start_time: int = 0
    end_time: int = 0
    limit: int = 0
    sort: str = ""

@dataclass
class Trade:
    trade_id: str
    order_id: str
    client_order_id: str
    symbol: str
    price: str
    qty: str
    quote_qty: str
    commission: str
    commission_asset: str
    is_buyer: bool
    is_maker: bool
    time: int