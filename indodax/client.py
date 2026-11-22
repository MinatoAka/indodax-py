from .http import MyHTTPClient
from .public import PublicAPI
from .private import PrivateAPI
from .exceptions import IndodaxError

class Client(PublicAPI, PrivateAPI):
    def __init__(self, api_key: str = "", secret_key: str = "", retries: int = 3, rate_limit: int = 5, timeout: int = 15):
        self.api_key = api_key
        self.secret_key = secret_key
        self.http = MyHTTPClient(retries=retries, rate_limit=rate_limit, timeout=timeout)

    def _check_status(self, resp):
        if resp.status_code != 200:
            try:
                data = resp.json()
                if "code" in data and "msg" in data:
                    raise IndodaxError(data["code"], data["msg"])
            except ValueError:
                pass
            raise Exception(f"HTTP {resp.status_code}: {resp.text}")