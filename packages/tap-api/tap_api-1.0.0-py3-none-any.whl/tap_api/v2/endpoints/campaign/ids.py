"""
Author: Ludvik Jerabek
Package: tap_api
License: MIT
"""
from typing import Optional

from tap_api.common.campaign.filters import TimeInterval
from tap_api.web import FilterOptions
from tap_api.web.resource import Resource
from .campaign_metadata import CampaignMetadata


class Ids(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)

    def __call__(self, interval: TimeInterval, page: Optional[int] = None,
                 size: Optional[int] = None) -> CampaignMetadata:
        if not isinstance(interval, TimeInterval):
            raise TypeError("`interval` must be an instance of TimeInterval.")
        if page is not None and page < 1:
            raise ValueError("`page` must be 1 or greater.")
        if size is not None and size < 1:
            raise ValueError("`size` must be 1 or greater.")

        options = FilterOptions()
        options.add_option("interval", interval.to_interval())
        options.add_option("page", page)
        options.add_option("size", size)
        return CampaignMetadata(self.session.get(self.uri, params=options.params))
