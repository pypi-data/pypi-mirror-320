import json

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TickerPO(Base):
    __tablename__ = 'ticker'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(12), unique=True, nullable=False)
    exchange = Column(String(8), nullable=False)
    quote_type = Column(String(8), nullable=False)
    short_name = Column(String(50), nullable=True)
    long_name = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "quote_type": self.quote_type,
            "short_name": self.short_name,
            "long_name": self.long_name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
