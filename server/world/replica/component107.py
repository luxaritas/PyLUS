"""
Component 107
"""

from pyraknet.bitstream import c_bit, c_int64

from .component import Component


class Component107(Component):
    """
    Component 107 class
    """
    def serialize(self, stream):
        stream.write(c_bit(True))  # NOTE: unknown
        stream.write(c_int64(0))

    def write_construction(self, stream):
        self.serialize(stream)
