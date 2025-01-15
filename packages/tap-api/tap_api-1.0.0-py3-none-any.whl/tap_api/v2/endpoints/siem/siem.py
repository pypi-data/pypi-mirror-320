"""
Author: Ludvik Jerabek
Package: tap_api
License: MIT
"""
from tap_api.web.resource import Resource


class Siem(Resource):

    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)
