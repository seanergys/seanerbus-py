# SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>
#
# SPDX-License-Identifier: MIT

import time
import datetime


class Time:
    """SEANERGYS timestamp standard object.
    Nanoseconds since 01.01.1970 00:00 UTC without leap seconds
    """

    timestamp: int

    @staticmethod
    def now() -> "Time":
        """Creates a SEANERGYS time object of the current time"""
        t = Time()
        t.timestamp = time.clock_gettime_ns(time.CLOCK_REALTIME)

        return t

    @staticmethod
    def from_ns(time_ns: int) -> "Time":
        """Creates a Time object from a number of nanoseconds

        :return: Time object representing that number of nanoseconds"""
        t = Time()
        t.timestamp = time_ns
        return t

    def to_ns(self) -> int:
        """Returns the number of nanoseconds in this time object

        :return: Number of nanoseconds"""
        return self.timestamp

    def to_datetime(self) -> datetime.datetime:
        """Converts the time object to a Python datetime.datetime object.

        The maximum resolution of datetime objects is generally one microseconds so this is a lossy conversion!"""
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.UTC) + datetime.timedelta(
            microseconds=self.timestamp / 1000
        )

    @staticmethod
    def from_datetime(dt: datetime.datetime) -> "Time":
        """Converts the datetime.datetime object given to a Time object"""
        dt = dt.astimezone(datetime.UTC)

        return Time.from_ns(
            int(
                (
                    dt - datetime.datetime(1970, 1, 1, tzinfo=datetime.UTC)
                ).total_seconds()
                * 10**9
            )
        )
