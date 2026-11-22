<div align="center">

# 🐍 indodax-py

**Standalone Python SDK for Official Indodax Trade API v2.**

*High-precision, blazing fast, and built with safety-first architecture.*

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/MinatoAka/indodax-py/ci.yml?branch=main&label=Tests&style=for-the-badge&logo=github)](https://github.com/MinatoAka/indodax-py/actions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](https://github.com/MinatoAka/indodax-py/pulls)

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

### 1. Initialize Client

Security best practice: **Never hardcode your credentials**. Use environment variables (e.g., from a `.env` file).

```python
import os
from indodax import Client

# 1. Load credentials from environment variables
API_KEY = os.getenv("INDODAX_API_KEY")
SECRET_KEY = os.getenv("INDODAX_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise ValueError("API credentials not found in environment variables!")

# 2. Initialize Client (customizable parameters)
client = Client(
    api_key=API_KEY, 
    secret_key=SECRET_KEY,
    
    # Optional parameters (defaults shown below):
    retries=3,                  # Auto-retry for GET requests on rate-limit/5xx
    rate_limit=5,               # Max 5 requests per second (anti-spam)
    timeout=15,                 # Request timeout in seconds
    user_agent="indodax-py/1.0" # Custom User-Agent
)
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

## 🤝 Support & Exchange

If this library helps you build profitable bots, consider supporting the development!

* 👉 [Daftar Akun Indodax](https://indodax.com/deeplink?page=register&id=AkaKen) (Referral)
* 👉 [Traktir Kopi](https://saweria.co/AKaAturDompet) ☕
