"""
This code was tested against Python 3.9
 
Author: Ludvik Jerabek
Package: tap_api
License: MIT
"""

from tap_api.v2.endpoints.campaign.campaign import Campaign
from tap_api.v2.endpoints.forensics.forensics import Forensics
from tap_api.v2.endpoints.people.people import People
from tap_api.v2.endpoints.siem.siem import Siem
from tap_api.v2.endpoints.threats.threat import Threat
from tap_api.v2.endpoints.url.url import Url

__all__ = ['Campaign', 'Forensics', 'People', 'Threat', 'Siem', 'Url']
