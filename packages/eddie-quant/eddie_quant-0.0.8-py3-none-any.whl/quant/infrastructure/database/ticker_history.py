from datetime import datetime, timedelta, timezone

from loguru import logger
from sqlalchemy.dialects.postgresql import insert

from quant.common.consts.time import TimeConfig
from quant.infrastructure.database.orm.ticker_history_po import TickerHistoryPO
from quant.infrastructure.database.engine import Engine


class TickerHistoryDatasourcePostgresql:
    def __init__(self, engine: Engine):
        self.__engine = engine
        self.__timezone_offset = timezone(timedelta(hours=-5))

    def insert(self, price_record: TickerHistoryPO):
        session = self.__engine.session()

        try:
            session.add(price_record)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting {price_record}: {e}")
            raise e
        finally:
            session.close()

    def m_insert(self, price_records: list[TickerHistoryPO]):
        session = self.__engine.session()

        try:
            records_to_insert = []
            for record in price_records:
                records_to_insert.append({
                    'symbol': record.symbol,
                    'time': record.time,
                    'interval': record.interval,
                    'open': record.open,
                    'high': record.high,
                    'low': record.low,
                    'close': record.close,
                    'volume': record.volume
                })

            stmt = insert(TickerHistoryPO).values(records_to_insert)
            stmt = stmt.on_conflict_do_nothing(index_elements=['symbol', 'time', 'interval'])

            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting records: {e}")
            raise e
        finally:
            session.close()

    def get_all(self, symbol: str) -> list[TickerHistoryPO]:
        session = self.__engine.session()

        try:
            history_records = session.query(TickerHistoryPO).filter(
                TickerHistoryPO.symbol == symbol,
            ).all()
            return history_records
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting all records: {e}, symbol: {symbol}")
            raise e
        finally:
            session.close()

    def get_by_date(self, symbol: str, start_date: str, end_date: str) -> list[TickerHistoryPO]:
        """
        get history by date, the date is in YYYY-MM-DD, use UTC-5 timezone
        :param symbol: str ticker symbol, e.g. 'AAPL'
        :param start_date: str '2025-01-02', inclusive
        :param end_date: str '2025-01-03', exclusive
        :return: list[History] list of price history records
        """
        session = self.__engine.session()
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=TimeConfig.DEFAULT_TIMEZONE)
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=TimeConfig.DEFAULT_TIMEZONE)
            history_records = session.query(TickerHistoryPO).filter(
                TickerHistoryPO.symbol == symbol,
                TickerHistoryPO.time >= start_datetime,
                TickerHistoryPO.time < end_datetime,
            ).all()
            return history_records
        except Exception as e:
            session.rollback()
            logger.error(
                f"Error getting records: {e}, symbol: {symbol}, symbol: {symbol},start_date: {start_date}, end_date: {end_date}")
            raise e
        finally:
            session.close()

    def get_latest(self, symbol: str) -> TickerHistoryPO:
        session = self.__engine.session()
        try:
            history_record = session.query(TickerHistoryPO).filter(
                TickerHistoryPO.symbol == symbol,
            ).order_by(TickerHistoryPO.time.desc()).first()
            return history_record
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting records: {e}, symbol: {symbol}")
            raise e
        finally:
            session.close()
