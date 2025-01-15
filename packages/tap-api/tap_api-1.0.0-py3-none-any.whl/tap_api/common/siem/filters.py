"""
Author: Ludvik Jerabek
Package: tap_api
License: MIT
"""
from enum import Enum


class SiemFormat(Enum):
    SYSLOG = 'syslog'
    JSON = 'json'


class SiemThreatType(Enum):
    URL = 'url'
    ATTACHMENT = 'attachment'
    MESSAGE_TEXT = 'messageText'


class SiemThreatStatus(Enum):
    ACTIVE = 'active'
    CLEARED = 'cleared'
    FALSE_POSITIVE = 'falsePositive'
