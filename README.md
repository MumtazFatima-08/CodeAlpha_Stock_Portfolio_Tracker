# CodeAlpha Portfolio Tracker

**Python-first portfolio management system** built for CodeAlpha Python Programming Internship — Task 2.

> The project treats a portfolio as a state derived from transaction history rather than as a collection of manually edited totals.

## Problem

A stock portfolio tracker needs to answer three questions correctly, even after many buys and partial sells of the same stock: how many shares do I own, what did they actually cost me on average, and what is my profit or loss right now versus what I've already locked in. This project implements that logic from first principles — no external portfolio libraries, no live market data — using a hardcoded price list, as specified by the CodeAlpha task.

## Features

- Record BUY and SELL transactions for a fixed set of tickers with hardcoded reference prices
- Automatic weighted-average cost basis across any number of buys
- Realized P/L on each sell, unrealized P/L against the current reference price
- Portfolio-level metrics: total invested, total value, overall return, best/worst holding
- Per-holding allocation percentage of the total portfolio
- Rejects invalid input: non-positive quantity/price, unknown tickers, overselling
- Optional CSV save/load of the full transaction history (`main.py` saves to `data/portfolio_transactions.csv` on every run)
- 20 unit tests covering the accounting logic and CSV persistence
- A small browser demo (see "Static web demo" below) for a GitHub Pages-hosted preview

## Technical implementation

- **`models.py`** — `Transaction` (frozen dataclass, immutable transaction record) and `Holding` (mutable per-ticker state with an `average_cost` property)
- **`validators.py`** — pure functions that validate ticker/quantity/price and raise domain-specific exceptions
- **`exceptions.py`** — a small exception hierarchy (`PortfolioError` → `ValidationError` → `UnknownTickerError`, and `InsufficientSharesError`) so callers can catch precisely what they need
- **`calculations.py`** — pure functions for market value, unrealized P/L, return %, and allocation %, kept separate from `Portfolio` so they're independently testable and reusable
- **`portfolio.py`** — the `Portfolio` class: owns a `dict[str, Holding]` for O(1) ticker lookup and a `list[Transaction]` as an append-only audit log; `buy()`/`sell()` apply validation and the weighted-average-cost rules
- **`storage.py`** — CSV save/load using the standard library `csv` module, with clear per-row error messages on malformed data
- **`prices.py`** — the hardcoded price dictionary required by the task spec

## Architecture

```text
User Input
    ↓
Validation
    ↓
Portfolio
    ↓
Transaction Processing
    ↓
Holdings / Cost Basis
    ↓
Calculations
    ↓
CSV Storage
```

And, separately, how the two halves of this repository relate:

```text
Python Core (portfolio_tracker/)
    ↓
Canonical Business Logic

Static Web Demo (web/)
    ↓
GitHub Pages-compatible presentation layer
```

The Python package is the canonical implementation and is what's covered by the test suite. `web/` is a lightweight, hand-written JavaScript mirror of the same weighted-average-cost math, kept only so the project can be previewed as a static page on GitHub Pages, which cannot execute a Python backend. It is not a second source of truth — see "Static web demo" below.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

python main.py
pytest -q
```

`pytest.ini` sets `pythonpath = .`, so `pytest -q` resolves the `portfolio_tracker` package correctly whether it's run directly or via `python -m pytest`.

To preview the browser UI, open `web/index.html` or serve the `web/` directory with any static server.

## Accounting model

Weighted-average cost is used for sells.

Example:

- Buy 10 TCS @ ₹3,000
- Buy 5 TCS @ ₹3,200
- Average cost = ₹46,000 / 15 = ₹3,066.67
- Sell 4 TCS @ ₹3,500
- Realized P/L = (₹3,500 − ₹3,066.67) × 4 ≈ ₹1,733.33

Remaining cost basis is reduced using the same average cost, and a sell for more shares than are owned raises `InsufficientSharesError` instead of allowing quantity to go negative.

## Static web demo

`web/` is a static HTML/CSS/JS page suitable for GitHub Pages. `app.js` recomputes holdings from an in-memory transaction list using the same weighted-average-cost formula as the Python package, purely so the page has something to render — it does not call into Python and is not tested by `pytest`. State lives only in the page's memory for the session; it is a demo layer, not a persistence layer.

## Testing

```text
20 passed
```

Run with `pytest -q` from the project root. Coverage includes: valid/invalid BUY and SELL, weighted-average cost across multiple buys, overselling rejection, realized and unrealized P/L, portfolio-level metrics, allocation percentages, and CSV round-tripping including malformed-CSV error handling (missing columns, non-numeric fields, invalid dates).

## Why this project exists

The CodeAlpha task is simple by design: accept stock names and quantities, use predefined prices, calculate total investment, and optionally save data. This implementation keeps that requirement but adds real engineering structure around it: domain modeling, validation, state transitions, persistence, calculations, and tests.

## Repository structure

```text
portfolio-tracker/
├── portfolio_tracker/
│   ├── models.py
│   ├── portfolio.py
│   ├── calculations.py
│   ├── prices.py
│   ├── storage.py
│   └── validators.py
├── tests/
├── web/
├── data/
├── main.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Interview talking points

1. **Why transactions instead of storing only totals?**
   Because transaction history is the source of truth and portfolio state can be reconstructed from it; totals alone would lose the audit trail and make weighted-average cost impossible to recompute correctly.

2. **Why use a dictionary for holdings?**
   Holdings are keyed by ticker and looked up on every buy/sell, so a `dict[str, Holding]` gives O(1)-average lookup instead of scanning a list.

3. **Why use a list for transaction history?**
   Transactions are an append-only, order-sensitive log — a list preserves insertion order naturally and matches how CSV rows are written and read back.

4. **Why weighted average cost?**
   It gives a single, deterministic cost basis for repeated buys and partial sells without the added bookkeeping of FIFO/LIFO lot tracking, while still producing a defensible realized P/L on every sell.

5. **How do you prevent overselling?**
   `Portfolio.sell()` checks the requested quantity against the current holding's quantity before mutating any state, and raises `InsufficientSharesError` if it isn't covered — the holding is left untouched on a rejected sell.

6. **Why separate calculations from portfolio state?**
   `calculations.py` holds pure functions (value, P/L, return %, allocation %) that take data in and return a number, with no side effects. That makes them trivial to unit test in isolation and reusable from both `Portfolio.snapshot()` and anywhere else that needs the same math.

7. **Why custom exceptions?**
   Domain errors such as overselling or an unknown ticker should be distinguishable from generic Python errors (`ValueError`, `KeyError`), so callers can catch `PortfolioError` (or a specific subclass) without accidentally swallowing unrelated bugs.

8. **Why hardcoded prices?**
   The internship specification asks for a predefined price dictionary rather than a live feed. Keeping prices deterministic also makes every test reproducible without mocking a network call.

9. **Why is Python the canonical implementation?**
   All validation, accounting rules, and tests live in `portfolio_tracker/`. It's the only version of the logic that's actually verified by the test suite.

10. **Why can't GitHub Pages run the Python backend directly?**
    GitHub Pages serves static files only — there's no server process to run a Python interpreter. The browser demo therefore reimplements the same math in JavaScript purely for presentation; it's clearly documented as a mirror, not a replacement, of the Python core.
