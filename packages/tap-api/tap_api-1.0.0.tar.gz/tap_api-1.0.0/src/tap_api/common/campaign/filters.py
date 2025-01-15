"""
Author: Ludvik Jerabek
Package: tap_api
License: MIT
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class TimeInterval(ABC):
    """
    Abstract base class for different types of time intervals.
    """
    _MIN_INTERVAL = timedelta(seconds=30)
    _MAX_INTERVAL = timedelta(days=1)

    def __init__(self):
        pass

    @abstractmethod
    def to_interval(self) -> str:
        """
        Generate an ISO 8601 interval string.
        Must be implemented by all subclasses.
        """
        pass

    def _validate_interval(self, duration: timedelta):
        """
        Validate that the duration is within the allowed range.
        """
        if not (self._MIN_INTERVAL <= duration <= self._MAX_INTERVAL):
            raise ValueError(
                f"Interval must be between {self._MIN_INTERVAL} and {self._MAX_INTERVAL}, but got {duration}."
            )


class StartEndInterval(TimeInterval):
    """
    Represents a time interval with a start and end time.

    For example:
    2020-05-01T12:00:00Z/2020-05-01T13:00:00Z - an hour interval, beginning at noon UTC on 05-01-2020
    """

    def __init__(self, start: datetime, end: datetime):
        super().__init__()
        duration = end - start
        self._validate_interval(duration)
        self.start = start
        self.end = end

    def to_interval(self) -> str:
        print(f"{self.start.isoformat()}/{self.end.isoformat()}")
        return f"{self.start.isoformat()}/{self.end.isoformat()}"


class StartOffsetInterval(TimeInterval):
    """
    Represents a time interval with a start time and a duration.

    For example:
    2020-05-01T12:00:00-0000/PT30M - The thirty minutes beginning at noon UTC on 05-01-2020 and ending at 12:30pm UTC
    """

    def __init__(self, start: datetime, offset: timedelta):
        super().__init__()
        self._validate_interval(offset)
        self.__start = start
        self.__offset = offset

    def to_interval(self) -> str:
        print(f"{self.__start.isoformat()}/{self.__format_interval(self.__offset)}")
        return f"{self.__start.isoformat()}/{self.__format_interval(self.__offset)}"

    def __format_interval(self, duration: timedelta) -> str:
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        duration_str = "P"
        if hours or minutes or seconds:
            duration_str += "T"
            if hours:
                duration_str += f"{hours}H"
            if minutes:
                duration_str += f"{minutes}M"
            if seconds:
                duration_str += f"{seconds}S"
        return duration_str


class OffsetEndInterval(TimeInterval):
    """
    Represents a time interval with a duration and an end time.

    For example:
    PT30M/2020-05-01T12:30:00-0000 - The thirty minutes beginning at noon UTC on 05-01-2020 and ending at 12:30pm UTC
    """

    def __init__(self, duration: timedelta, end: datetime):
        super().__init__()
        self._validate_interval(duration)
        self.__offset = duration
        self.__end = end

    def to_interval(self) -> str:
        print(f"{self.__format_interval(self.__offset)}/{self.__end.isoformat()}")
        return f"{self.__format_interval(self.__offset)}/{self.__end.isoformat()}"

    def __format_interval(self, duration: timedelta) -> str:
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        duration_str = "P"
        if hours or minutes or seconds:
            duration_str += "T"
            if hours:
                duration_str += f"{hours}H"
            if minutes:
                duration_str += f"{minutes}M"
            if seconds:
                duration_str += f"{seconds}S"
        return duration_str
