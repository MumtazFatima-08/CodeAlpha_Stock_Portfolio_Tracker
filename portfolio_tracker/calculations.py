from .models import Holding

def market_value(holding: Holding, current_price: float) -> float:
    return holding.quantity * current_price

def unrealized_pnl(holding: Holding, current_price: float) -> float:
    return market_value(holding, current_price) - holding.cost_basis

def return_percent(holding: Holding, current_price: float) -> float:
    if holding.cost_basis == 0:
        return 0.0
    return unrealized_pnl(holding, current_price) / holding.cost_basis * 100

def allocation_percent(value: float, total_value: float) -> float:
    return value / total_value * 100 if total_value else 0.0
