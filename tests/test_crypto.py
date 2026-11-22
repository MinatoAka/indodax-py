import pytest
from indodax.crypto import build_query, sign_sha256

def test_build_query_sorts_and_encodes():
    # Input acak (tidak berurutan)
    params = {
        "symbol": "btcidr",
        "limit": "100",
        "timestamp": "1578304294000",
        "recvWindow": "5000"
    }
    
    expected = "limit=100&recvWindow=5000&symbol=btcidr&timestamp=1578304294000"
    
    # Fungsi harus mengurutkan berdasarkan abjad (limit, recvWindow, symbol, timestamp)
    assert build_query(params) == expected

def test_sign_sha256_exact_match():
    # Data uji dari dokumentasi resmi Indodax
    secret_key = "f60617a68fcce028f0a90bc9eb765d17379eb548cc935c01a7ee3186eecf870e9b68f27a31bcfe8d"
    payload = "symbol=btcidr&limit=100&timestamp=1578304294000&recvWindow=5000"
    
    # Signature yang seharusnya dihasilkan (dari doc Indodax)
    expected_sig = "58b503019a8f2754af7097b4d981913a8dca9e5cb2b408061cbd48736a940558"
    
    assert sign_sha256(payload, secret_key) == expected_sig