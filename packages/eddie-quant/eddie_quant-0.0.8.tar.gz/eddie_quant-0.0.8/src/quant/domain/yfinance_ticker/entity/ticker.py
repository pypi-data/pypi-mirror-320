import json
from dataclasses import dataclass


@dataclass
class Ticker:
    symbol: str
    exchange: str
    quote_type: str
    short_name: str
    long_name: str

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "exchange": self.exchange,
            "quote_type": self.quote_type,
            "short_name": self.short_name,
            "long_name": self.long_name,
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
