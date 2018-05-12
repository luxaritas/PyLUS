"""
World loading utilities
"""

from enums import ZONE_LUZ
from plugin import Plugin, Action
from luzreader import LUZReader


class WorldUtil(Plugin):
    """
    World loading utlity class
    """
    cache = {}

    def actions(self):
        """
        Returns the actions
        """
        return [
            Action('world:get_zone_luz', self.get_zone_luz, 10),
        ]

    def packets(self):
        """
        Returns the packets
        """
        return []

    def get_zone_luz(self, zone):
        luz = self.cache[zone] if zone in self.cache else LUZReader(ZONE_LUZ[zone])

        if zone not in self.cache:
            self.cache[zone] = luz

        return luz
