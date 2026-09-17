class PortfolioError(Exception):
    """Base domain error."""

class ValidationError(PortfolioError):
    """Raised when transaction input is invalid."""

class UnknownTickerError(ValidationError):
    """Raised for unsupported tickers."""

class InsufficientSharesError(PortfolioError):
    """Raised when a sell exceeds the current holding."""
