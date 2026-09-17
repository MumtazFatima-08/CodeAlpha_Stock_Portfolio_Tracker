from .exceptions import UnknownTickerError, ValidationError
from .prices import STOCK_PRICES

def validate_ticker(ticker: str) -> str:
    value = ticker.strip().upper()
    if not value:
        raise ValidationError("Ticker is required.")
    if value not in STOCK_PRICES:
        raise UnknownTickerError(f"Unsupported ticker: {value}")
    return value

def validate_quantity(quantity: int) -> int:
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValidationError("Quantity must be a positive whole number.")
    return quantity

def validate_price(price: float) -> float:
    if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:
        raise ValidationError("Price must be greater than zero.")
    return float(price)
