import csv
from datetime import date
from pathlib import Path
from .models import Transaction

FIELDS = ["ticker", "transaction_type", "quantity", "price", "transaction_date"]

def save_transactions(transactions: list[Transaction], path: str | Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for tx in transactions:
            writer.writerow({
                "ticker": tx.ticker,
                "transaction_type": tx.transaction_type,
                "quantity": tx.quantity,
                "price": tx.price,
                "transaction_date": tx.transaction_date.isoformat(),
            })

def load_transactions(path: str | Path) -> list[Transaction]:
    transactions = []
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = set(FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")
        for line_number, row in enumerate(reader, start=2):  # header is line 1
            try:
                transactions.append(Transaction(
                    ticker=row["ticker"].strip().upper(),
                    transaction_type=row["transaction_type"].strip().upper(),
                    quantity=int(row["quantity"]),
                    price=float(row["price"]),
                    transaction_date=date.fromisoformat(row["transaction_date"]),
                ))
            except (KeyError, ValueError) as error:
                raise ValueError(f"Malformed CSV row at line {line_number}: {error}") from error
    return transactions
