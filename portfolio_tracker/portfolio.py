from datetime import date
from .calculations import market_value, unrealized_pnl, return_percent, allocation_percent
from .exceptions import InsufficientSharesError
from .models import Holding, Transaction
from .prices import STOCK_PRICES
from .validators import validate_price, validate_quantity, validate_ticker

class Portfolio:
    """Maintains portfolio state by applying validated transactions."""

    def __init__(self) -> None:
        self.transactions: list[Transaction] = []
        self._holdings: dict[str, Holding] = {}

    def buy(self, ticker: str, quantity: int, price: float, transaction_date: date | None = None) -> None:
        ticker = validate_ticker(ticker)
        quantity = validate_quantity(quantity)
        price = validate_price(price)
        holding = self._holdings.setdefault(ticker, Holding(ticker=ticker))
        holding.quantity += quantity
        holding.cost_basis += quantity * price
        self.transactions.append(Transaction(ticker, "BUY", quantity, price, transaction_date or date.today()))

    def sell(self, ticker: str, quantity: int, price: float, transaction_date: date | None = None) -> None:
        ticker = validate_ticker(ticker)
        quantity = validate_quantity(quantity)
        price = validate_price(price)
        holding = self._holdings.get(ticker)
        if not holding or quantity > holding.quantity:
            owned = holding.quantity if holding else 0
            raise InsufficientSharesError(f"Cannot sell {quantity} {ticker}; only {owned} owned.")

        average_cost = holding.average_cost
        holding.realized_pnl += (price - average_cost) * quantity
        holding.cost_basis -= average_cost * quantity
        holding.quantity -= quantity
        self.transactions.append(Transaction(ticker, "SELL", quantity, price, transaction_date or date.today()))
        if holding.quantity == 0:
            del self._holdings[ticker]

    def get_holdings(self) -> list[Holding]:
        return list(self._holdings.values())

    def snapshot(self) -> list[dict]:
        total_value = sum(market_value(h, STOCK_PRICES[h.ticker]) for h in self.get_holdings())
        rows = []
        for h in self.get_holdings():
            price = STOCK_PRICES[h.ticker]
            value = market_value(h, price)
            pnl = unrealized_pnl(h, price)
            rows.append({
                "ticker": h.ticker,
                "quantity": h.quantity,
                "average_cost": h.average_cost,
                "current_price": price,
                "invested": h.cost_basis,
                "value": value,
                "pnl": pnl,
                "pnl_percent": return_percent(h, price),
                "allocation": allocation_percent(value, total_value),
                "realized_pnl": h.realized_pnl,
            })
        return rows

    def metrics(self) -> dict:
        rows = self.snapshot()
        invested = sum(r["invested"] for r in rows)
        value = sum(r["value"] for r in rows)
        pnl = value - invested
        best = max(rows, key=lambda r: r["pnl_percent"], default=None)
        worst = min(rows, key=lambda r: r["pnl_percent"], default=None)
        return {
            "invested": invested,
            "value": value,
            "pnl": pnl,
            "return_percent": pnl / invested * 100 if invested else 0.0,
            "holdings": len(rows),
            "best": best["ticker"] if best else "-",
            "worst": worst["ticker"] if worst else "-",
        }
