import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from quant.common.consts.time import TimeConfig


@dataclass
class TickerHistory:
    symbol: str
    time: datetime
    interval: str

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "time": self.time.astimezone(TimeConfig.DEFAULT_TIMEZONE).isoformat() if self.time else None,
            "interval": self.interval,
            "open": float(self.open) if self.open else None,
            "high": float(self.high) if self.high else None,
            "low": float(self.low) if self.low else None,
            "close": float(self.close) if self.close else None,
            "volume": float(self.volume) if self.volume else None,
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
