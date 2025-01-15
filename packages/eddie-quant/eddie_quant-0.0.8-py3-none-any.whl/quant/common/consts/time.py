import datetime
from datetime import timedelta, timezone
from enum import Enum
from typing import Final


class Interval(Enum):
    INTERVAL_1m = "1m"
    INTERVAL_2m = "2m"
    INTERVAL_5m = "5m"
    INTERVAL_15m = "15m"
    INTERVAL_30m = "30m"
    INTERVAL_60m = "60m"
    INTERVAL_90m = "90m"
    INTERVAL_1h = "1h"
    INTERVAL_1d = "1d"


class TimeConfig:
    """
    By default, the timezone is set to UTC-5, America/New_York.
    """
    DEFAULT_TIMEZONE: Final[datetime.tzinfo] = timezone(timedelta(hours=-5))

    """
    By default, the start date is 2000-01-01
    """
    DEFAULT_START_DATE: Final[str] = "2000-01-01"

    DEFAULT_DATE_FORMAT: Final[str] = "%Y-%m-%d"
