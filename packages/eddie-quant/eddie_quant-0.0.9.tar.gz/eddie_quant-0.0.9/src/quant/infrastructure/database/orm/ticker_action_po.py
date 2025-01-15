import json

from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TickerActionPO(Base):
    __tablename__ = 'ticker_action'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(12), nullable=False)
    time = Column(TIMESTAMP(timezone=True), nullable=False)
    dividend = Column(Numeric, nullable=False)
    stock_split = Column(Numeric, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), default=func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "time": self.time,
            "dividend": self.dividend,
            "stock_split": self.stock_split,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
