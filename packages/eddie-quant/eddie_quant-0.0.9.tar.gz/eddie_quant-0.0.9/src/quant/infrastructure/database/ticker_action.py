from datetime import timezone, timedelta, datetime
from typing import Optional

from loguru import logger
from sqlalchemy.dialects.postgresql import insert

from quant.common.consts.time import TimeConfig
from quant.infrastructure.database.engine import Engine
from quant.infrastructure.database.orm.ticker_action_po import TickerActionPO


class TickerActionDatasourcePostgresql:
    def __init__(self, engine: Engine):
        self.__engine = engine
        self.__timezone_offset = timezone(timedelta(hours=-5))

    def insert(self, record: TickerActionPO):
        session = self.__engine.session()

        try:
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting {record}: {e}")
            raise e
        finally:
            session.close()

    def m_insert(self, records: list[TickerActionPO]):
        session = self.__engine.session()
        try:
            records_to_insert = []
            for record in records:
                records_to_insert.append({
                    'symbol': record.symbol,
                    'time': record.time,
                    'dividend': record.dividend,
                    'stock_split': record.stock_split,
                })

            stmt = insert(TickerActionPO).values(records_to_insert)
            stmt = stmt.on_conflict_do_nothing(index_elements=['symbol', 'time'])

            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting records: {e}")
            raise e
        finally:
            session.close()

    def get_all(self, symbol: str) -> list[TickerActionPO]:
        session = self.__engine.session()

        try:
            records = session.query(TickerActionPO).filter(TickerActionPO.symbol == symbol).all()
            return records
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting records: {e}, symbol: {symbol}")
            raise e
        finally:
            session.close()

    def get_by_date(self, symbol: str, start_date: str, end_date: str) -> list[TickerActionPO]:
        session = self.__engine.session()

        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=TimeConfig.DEFAULT_TIMEZONE)
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=TimeConfig.DEFAULT_TIMEZONE)
            records = session.query(TickerActionPO).filter(
                TickerActionPO.symbol == symbol,
                TickerActionPO.time >= start_datetime,
                TickerActionPO.time < end_datetime,
            ).all()
            return records
        except Exception as e:
            session.rollback()
            logger.error(
                f"Error getting records: {e}, symbol: {symbol}, start_date: {start_date}, end_date: {end_date}")
            raise e
        finally:
            session.close()

    def get_latest(self, symbol: str) -> Optional[TickerActionPO]:
        session = self.__engine.session()

        try:
            record = session.query(TickerActionPO).filter(
                TickerActionPO.symbol == symbol,
            ).order_by(TickerActionPO.time.desc()).first()
            return record
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting records: {e}, symbol: {symbol}")
            raise e
        finally:
            session.close()
