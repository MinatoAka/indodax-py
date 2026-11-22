class IndodaxError(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"indodax api error (code {code}): {msg}")

    def is_rate_limit(self) -> bool: return self.code == -1003
    def is_invalid_credentials(self) -> bool: return self.code in (-1002, -2014)
    def is_invalid_timestamp(self) -> bool: return self.code == -1021
    def is_invalid_signature(self) -> bool: return self.code == -1022
    def is_insufficient_balance(self) -> bool: return self.code == -4026
    def is_order_not_found(self) -> bool: return self.code in (-2013, 1112)
    def is_market_suspended(self) -> bool: return self.code == -1016
    def is_order_rejected(self) -> bool: return self.code == -2010
    def is_access_blocked(self) -> bool: return self.code == -2015