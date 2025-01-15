from datetime import datetime

from quant.common.consts.time import TimeConfig


class TimeUtil:

    @staticmethod
    def get_date_str(time: datetime) -> str:
        """
        convert datetime to string, in format yyyy-mm-dd, use TimeConfig.DEFAULT_TIMEZONE
        :param time: time to convert
        :type time: datetime
        :return: date string, in format yyyy-mm-dd
        :rtype: string
        """
        return time.astimezone(TimeConfig.DEFAULT_TIMEZONE).strftime(
            TimeConfig.DEFAULT_DATE_FORMAT)
