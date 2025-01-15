"""
Author: Ludvik Jerabek
Package: tap_api
License: MIT
"""
from enum import Enum


class TimeWindow(Enum):
    DAYS_14 = 14
    DAYS_30 = 30
    DAYS_90 = 90
