import time
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class MyHTTPClient:
    def __init__(self, retries=3, backoff_factor=1.0, rate_limit=5, timeout=15, user_agent="indodax-py/1.0"):
        if rate_limit <= 0:
            rate_limit = 5
        self.timeout = timeout
        self.rate_limit_interval = 1.0 / rate_limit
        self.last_request_time = 0.0
        self.lock = threading.Lock()
        
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

        # HARDCODE: POST TIDAK PERNAH DI-RETRY demi keamanan
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"], # <-- Hanya method aman
            respect_retry_after_header=True,
            backoff_jitter=0.5
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _rate_limit_wait(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_request_time
            if elapsed < self.rate_limit_interval:
                time.sleep(self.rate_limit_interval - elapsed)
            self.last_request_time = time.time()

    def request(self, method, url, **kwargs):
        self._rate_limit_wait()
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self.session.request(method, url, **kwargs)