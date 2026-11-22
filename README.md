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
