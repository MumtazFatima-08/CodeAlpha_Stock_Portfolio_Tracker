from pathlib import Path

from portfolio_tracker.portfolio import Portfolio
from portfolio_tracker.exceptions import PortfolioError
from portfolio_tracker.storage import save_transactions

DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_FILE = DATA_DIR / "portfolio_transactions.csv"

def run_demo() -> None:
    portfolio = Portfolio()
    portfolio.buy("TCS", 10, 3000)
    portfolio.buy("TCS", 5, 3200)
    portfolio.buy("INFY", 8, 1500)
    portfolio.sell("TCS", 4, 3500)

    print("\nCODEALPHA PORTFOLIO TRACKER")
    print("-" * 70)
    for row in portfolio.snapshot():
        print(f"{row['ticker']:10} Qty: {row['quantity']:>4}  Value: ₹{row['value']:>10,.2f}  P/L: ₹{row['pnl']:>9,.2f}")
    print("-" * 70)
    for key, value in portfolio.metrics().items():
        print(f"{key:16}: {value:.2f}" if isinstance(value, float) else f"{key:16}: {value}")

    # Optional file saving, as required by the CodeAlpha task spec.
    DATA_DIR.mkdir(exist_ok=True)
    save_transactions(portfolio.transactions, OUTPUT_FILE)
    print(f"\nSaved {len(portfolio.transactions)} transactions -> {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        run_demo()
    except PortfolioError as error:
        print(f"Portfolio error: {error}")
