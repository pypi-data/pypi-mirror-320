import json
from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric
from sqlalchemy import Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from quant.common.consts.time import TimeConfig

Base = declarative_base()


class TickerHistoryPO(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(12), nullable=False)
    time = Column(TIMESTAMP(timezone=True), nullable=False)
    interval = Column(String(3), nullable=False)

    open = Column(Numeric, nullable=True)
    high = Column(Numeric, nullable=True)
    low = Column(Numeric, nullable=True)
    close = Column(Numeric, nullable=True)
    volume = Column(Numeric, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), default=func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "time": self.time.astimezone(TimeConfig.DEFAULT_TIMEZONE).isoformat() if self.time else None,
            "interval": self.interval,
            "open": float(self.open) if self.open else None,
            "high": float(self.high) if self.high else None,
            "low": float(self.low) if self.low else None,
            "close": float(self.close) if self.close else None,
            "volume": float(self.volume) if self.volume else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)


Index('idx_history_symbol', TickerHistoryPO.symbol)
Index('idx_history_symbol_time_interval', TickerHistoryPO.symbol, TickerHistoryPO.time, TickerHistoryPO.interval)
