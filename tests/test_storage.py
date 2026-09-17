import pytest
from datetime import date
from portfolio_tracker.models import Transaction
from portfolio_tracker.storage import load_transactions, save_transactions

def test_csv_round_trip(tmp_path):
    source = [Transaction("TCS", "BUY", 2, 3000.0, date(2026, 9, 15))]
    path = tmp_path / "transactions.csv"
    save_transactions(source, path)
    assert load_transactions(path) == source

def test_round_trip_preserves_multiple_transactions_in_order(tmp_path):
    source = [
        Transaction("TCS", "BUY", 10, 3000.0, date(2026, 9, 10)),
        Transaction("TCS", "BUY", 5, 3200.0, date(2026, 9, 11)),
        Transaction("INFY", "BUY", 8, 1500.0, date(2026, 9, 12)),
        Transaction("TCS", "SELL", 4, 3500.0, date(2026, 9, 13)),
    ]
    path = tmp_path / "transactions.csv"
    save_transactions(source, path)
    assert load_transactions(path) == source

def test_missing_columns_are_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("ticker,quantity,price\nTCS,10,3000\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing CSV columns"):
        load_transactions(path)

def test_non_numeric_quantity_is_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "ticker,transaction_type,quantity,price,transaction_date\n"
        "TCS,BUY,ten,3000,2026-09-10\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Malformed CSV row at line 2"):
        load_transactions(path)

def test_invalid_date_is_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "ticker,transaction_type,quantity,price,transaction_date\n"
        "TCS,BUY,10,3000,not-a-date\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Malformed CSV row at line 2"):
        load_transactions(path)
