from dataclasses import dataclass
from datetime import date
from typing import Literal

TransactionType = Literal["BUY", "SELL"]

@dataclass(frozen=True)
class Transaction:
    ticker: str
    transaction_type: TransactionType
    quantity: int
    price: float
    transaction_date: date

@dataclass
class Holding:
    ticker: str
    quantity: int = 0
    cost_basis: float = 0.0
    realized_pnl: float = 0.0

    @property
    def average_cost(self) -> float:
        return self.cost_basis / self.quantity if self.quantity else 0.0
