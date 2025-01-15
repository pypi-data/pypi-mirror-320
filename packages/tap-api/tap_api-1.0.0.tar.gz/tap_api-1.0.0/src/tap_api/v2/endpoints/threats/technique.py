"""
Author: Ludvik Jerabek
Package: tap_api
License: MIT
"""
from typing import Dict


class Technique(Dict):
    @property
    def id(self) -> str:
        return self.get("id", "")

    @property
    def name(self) -> str:
        return self.get("name", "")
