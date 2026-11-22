import hmac
import hashlib
import urllib.parse

def build_query(params: dict) -> str:
    """Mengurutkan key secara alfabet dan meng-encode-nya."""
    return urllib.parse.urlencode(sorted(params.items()))

def sign_sha256(payload: str, secret_key: str) -> str:
    """Membuat signature HMAC-SHA256."""
    return hmac.new(
        secret_key.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()