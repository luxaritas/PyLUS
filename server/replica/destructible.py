"""
Destructible component
"""

from pyraknet.bitstream import c_bit
from .component import Component


class Destructible(Component):
    """
    Destructible component class
    """
    def write_construction(self, stream):
        stream.write(c_bit(False))  # NOTE: unknown flag(?)
        stream.write(c_bit(False))  # NOTE: unknown flag

    def serialize(self, stream):
        pass
