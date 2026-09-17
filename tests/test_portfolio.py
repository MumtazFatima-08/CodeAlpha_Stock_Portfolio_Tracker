import pytest
from portfolio_tracker.portfolio import Portfolio
from portfolio_tracker.exceptions import InsufficientSharesError, UnknownTickerError, ValidationError

def test_valid_buy_creates_a_holding():
    p = Portfolio()
    p.buy("TCS", 10, 3000)
    row = p.snapshot()[0]
    assert row["ticker"] == "TCS"
    assert row["quantity"] == 10
    assert row["invested"] == pytest.approx(30000)

def test_multiple_buys_use_weighted_average_cost():
    p = Portfolio()
    p.buy("TCS", 10, 3000)
    p.buy("TCS", 5, 3200)
    row = p.snapshot()[0]
    assert row["average_cost"] == pytest.approx(3066.6666667)
    assert row["invested"] == pytest.approx(46000)

def test_sell_reduces_quantity_and_records_realized_pnl():
    p = Portfolio()
    p.buy("TCS", 10, 3000)
    p.sell("TCS", 4, 3500)
    row = p.snapshot()[0]
    assert row["quantity"] == 6
    assert row["realized_pnl"] == pytest.approx(2000)

def test_sell_after_multiple_buys_uses_weighted_average_for_realized_pnl():
    # BUY 10 @ 3000, BUY 5 @ 3200 -> avg cost ~3066.67
    # SELL 4 @ 3500 -> realized P/L = (3500 - 3066.67) * 4 ~= 1733.33
    p = Portfolio()
    p.buy("TCS", 10, 3000)
    p.buy("TCS", 5, 3200)
    p.sell("TCS", 4, 3500)
    row = p.snapshot()[0]
    assert row["quantity"] == 11
    assert row["average_cost"] == pytest.approx(3066.6666667)
    assert row["realized_pnl"] == pytest.approx(1733.3333333)
    # Remaining cost basis must still reflect the same average cost per share.
    assert row["invested"] == pytest.approx(row["average_cost"] * row["quantity"])

def test_selling_full_position_removes_the_holding():
    p = Portfolio()
    p.buy("TCS", 5, 3000)
    p.sell("TCS", 5, 3200)
    assert p.snapshot() == []
    assert p.get_holdings() == []

def test_oversell_is_rejected():
    p = Portfolio()
    p.buy("INFY", 3, 1500)
    with pytest.raises(InsufficientSharesError):
        p.sell("INFY", 4, 1600)
    # A failed sell must not mutate the holding.
    row = p.snapshot()[0]
    assert row["quantity"] == 3

def test_selling_a_ticker_never_owned_is_rejected():
    p = Portfolio()
    with pytest.raises(InsufficientSharesError):
        p.sell("TCS", 1, 3000)

def test_invalid_quantity_is_rejected():
    p = Portfolio()
    with pytest.raises(ValidationError):
        p.buy("TCS", 0, 3000)

def test_negative_quantity_is_rejected():
    p = Portfolio()
    with pytest.raises(ValidationError):
        p.buy("TCS", -5, 3000)

def test_invalid_price_is_rejected():
    p = Portfolio()
    with pytest.raises(ValidationError):
        p.buy("TCS", 1, 0)
    with pytest.raises(ValidationError):
        p.buy("TCS", 1, -100)

def test_unknown_ticker_is_rejected():
    p = Portfolio()
    with pytest.raises(UnknownTickerError):
        p.buy("FAKE", 2, 100)

def test_unrealized_pnl_reflects_current_market_price():
    p = Portfolio()
    p.buy("INFY", 8, 1500)  # current price is 1650 in prices.py
    row = p.snapshot()[0]
    assert row["current_price"] == 1650
    assert row["value"] == pytest.approx(8 * 1650)
    assert row["pnl"] == pytest.approx((1650 - 1500) * 8)

def test_allocation_percent_sums_to_100_across_holdings():
    p = Portfolio()
    p.buy("TCS", 10, 3000)
    p.buy("INFY", 8, 1500)
    rows = p.snapshot()
    assert sum(r["allocation"] for r in rows) == pytest.approx(100)

def test_portfolio_metrics_aggregate_across_holdings():
    p = Portfolio()
    p.buy("TCS", 10, 3000)
    p.buy("INFY", 8, 1500)
    metrics = p.metrics()
    assert metrics["holdings"] == 2
    assert metrics["invested"] == pytest.approx(30000 + 12000)
    assert metrics["value"] == pytest.approx(10 * 3500 + 8 * 1650)
    assert metrics["pnl"] == pytest.approx(metrics["value"] - metrics["invested"])

def test_metrics_on_empty_portfolio_do_not_divide_by_zero():
    p = Portfolio()
    metrics = p.metrics()
    assert metrics["holdings"] == 0
    assert metrics["return_percent"] == 0.0
    assert metrics["best"] == "-"
    assert metrics["worst"] == "-"
