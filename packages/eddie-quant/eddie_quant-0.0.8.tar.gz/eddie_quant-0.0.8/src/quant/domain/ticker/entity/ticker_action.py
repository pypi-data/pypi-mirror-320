import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class TickerAction:
    id: int
    symbol: str
    time: datetime
    dividend: Decimal
    stock_split: Decimal

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "time": self.time,
            "dividend": self.dividend,
            "stock_split": self.stock_split,
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
