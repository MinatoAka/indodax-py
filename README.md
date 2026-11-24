<div align="center">

# 🐍 indodax-py

**Standalone Python SDK for Official Indodax Trade API v2.**

*High-precision, blazing fast, and built with safety-first architecture.*

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](https://github.com/MinatoAka/indodax-py/pulls)
[![Saweria](https://img.shields.io/badge/Saweria-Support%20Me-FB6D26?style=for-the-badge)](https://saweria.co/AKaAturDompet)
[![Python CI](https://github.com/MinatoAka/indodax-py/actions/workflows/ci.yml/badge.svg?style=for-the-badge)](https://github.com/MinatoAka/indodax-py/actions/workflows/ci.yml)

</div>

---

## ⚡ Why indodax-py?

Most trading libraries are built for general purposes and ignore exchange-specific edge cases. `indodax-py` is engineered specifically for **real-world algorithmic trading bots** in Python.

| Feature | Implementation |
| :--- | :--- |
| 🎯 **Maximum Precision** | Balances are returned as raw strings (`asset_raw`). No lossy float conversions at the SDK layer. |
| 🛡️ **Anti Double-Order** | `POST` requests are **never** retried automatically. Prevents catastrophic duplicate executions on network timeouts. |
| 🔄 **Smart Rate Limiting** | Safe GET requests utilize exponential backoff, jitter, and automatic `Retry-After` header respect. |
| 🧠 **Typed Error Handling** | Catch errors gracefully using `IndodaxError` with helper methods like `.is_rate_limit()` or `.is_invalid_signature()`. |

## 📦 Installation

Since the library is currently hosted on GitHub, install it directly via `pip`:

```bash
pip install git+https://github.com/MinatoAka/indodax-py.git
```

## 🚀 Quick Start

### 1. Read Public Market Data

Public endpoints do not require API credentials:

```python
from indodax import Client

client = Client(
    # Optional parameters (defaults shown below):
    retries=3,
    rate_limit=5,
    timeout=15,
    user_agent="indodax-py/1.0",
)

# Get a ticker
ticker = client.get_ticker("ethidr")

print("Last:", ticker.ticker.last)
print("Buy:", ticker.get_highest_bid())
print("Sell:", ticker.get_lowest_ask())
print("24h high:", ticker.get_day_high())
print("24h low:", ticker.get_day_low())

# List available pairs
pairs = client.get_pairs()
for pair in pairs:
    print(pair.id, "min_qty=", pair.min_qty)
```

`Client()` can be used without credentials for `get_ticker()` and `get_pairs()`.

### 2. Initialize the Private API

Private endpoints require API credentials. Security best practice: **never hardcode credentials**. Load them from environment variables instead.

```python
import os
from indodax import Client

API_KEY = os.getenv("INDODAX_API_KEY")
SECRET_KEY = os.getenv("INDODAX_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise ValueError("API credentials not found in environment variables!")

client = Client(
    api_key=API_KEY,
    secret_key=SECRET_KEY,

    # Optional parameters (defaults shown below):
    retries=3,
    rate_limit=5,
    timeout=15,
    user_agent="indodax-py/1.0",
)
```

### 3. Check Balances

```python
balances = client.get_balances("ethidr")

print("IDR balance:", balances.idr)
print("ETH balance:", balances.asset)
print("ETH balance (raw):", balances.asset_raw)
```

`asset_raw` preserves the exchange's original string value, so it is suitable for calculations that require no precision loss.

### 4. Submit Market Orders

> **Market orders execute immediately.** Run only after validating balances and trading requirements.

```python
# Buy ETH using 100,000 IDR
buy_order = client.place_market_buy("ethidr", 100_000.00)

print("Buy order ID:", buy_order.order_id)
print("Full order ID:", buy_order.full_order_id)

# Sell 0.00030391 ETH
sell_order = client.place_market_sell(
    "ethidr",
    "0.00030391",
)

print("Sell order ID:", sell_order.order_id)
```

Market buy amounts are formatted as a two-decimal string internally. Market sell quantities should be passed as a string to preserve precision.

### 5. Get Trade History

```python
from indodax import TradeHistoryRequest

trade_history = client.trade_history(
    TradeHistoryRequest(
        symbol="ETHIDR",
        limit=20,
    )
)

for trade in trade_history:
    print(
        trade.trade_id,
        trade.price,
        trade.qty,
        trade.commission,
    )
```

### 6. Handle API Errors

```python
from indodax import IndodaxError

try:
    balances = client.get_balances("ethidr")
except IndodaxError as error:
    if error.is_invalid_signature():
        print("Invalid API signature. Check your secret key.")
    elif error.is_invalid_credentials():
        print("Invalid API credentials.")
    elif error.is_rate_limit():
        print("Rate limit reached. Please wait before retrying.")
    elif error.is_insufficient_balance():
        print("Insufficient balance.")
    else:
        print(error)
```

## 📂 Project Structure

```text
indodax-py/
├── indodax/               # Main package
│   ├── __init__.py        # Public exports (Client, Models, Exceptions)
│   ├── client.py          # Main entry point (Mixin combiner)
│   ├── public.py          # Public endpoints (Ticker, Pairs)
│   ├── private.py         # Private endpoints (Balances, Orders, Trades)
│   ├── models.py          # Dataclasses (OrderResult, BalanceResult, etc.)
│   ├── exceptions.py      # Typed API errors (IndodaxError)
│   ├── http.py            # HTTP layer (MyHTTPClient with retry & rate limit)
│   └── crypto.py          # Cryptography (HMAC-SHA256 signing)
├── tests/                 # Unit tests (pytest + requests-mock)
│   └── test_client.py
├── pyproject.toml         # Build & dependencies config
└── README.md
```

### Design Philosophy

* Separation of Concerns: HTTP, Crypto, and API Endpoints are strictly separated into distinct files. No monolithic spaghetti code.
* Mixin Architecture: PublicAPI and PrivateAPI are mixed into the main Client, keeping endpoints organized without relying on inheritance bloat.

## 🛠️ Architecture & Design Choices

<table>
  <tr>
    <td><b>Component</b></td>
    <td><b>Implementation</b></td>
    <td><b>Reasoning</b></td>
  </tr>
  <tr>
    <td><b>HTTP Layer</b></td>
    <td>Custom <code>MyHTTPClient</code> (requests + urllib3)</td>
    <td>Provides myhttp-like resilience without external heavy dependencies.</td>
  </tr>
  <tr>
    <td><b>Data Models</b></td>
    <td><code>@dataclass</code> with string-based numbers</td>
    <td>Prevents Python's float inaccuracies from affecting exchange math.</td>
  </tr>
  <tr>
    <td><b>Security</b></td>
    <td>No Withdrawal endpoints provided</td>
    <td>Security by design. Limits blast radius if API keys are compromised.</td>
  </tr>
</table>


## 🕵️ Reference

* [Standalone Library Go Indodax API](https://github.com/MinatoAka/indodax-go)
* [Indodax Official Api Docs](https://github.com/btcid/indodax-official-api-docs)


## 🤝 Support & Exchange

If this library helps you build profitable bots, consider supporting the development!

* 👉 [Daftar Akun Indodax](https://indodax.com/deeplink?page=register&id=AkaKen) (Referral)
* 👉 [Traktir Kopi](https://saweria.co/AKaAturDompet) ☕
