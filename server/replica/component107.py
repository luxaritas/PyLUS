"""
Component 107
"""

from pyraknet.bitstream import c_bit

from replica.component import Component


class Component107(Component):
    """
    Component 107 class
    """
    def serialize(self, stream):
        stream.write(c_bit(False))  # NOTE: unknown

    def write_construction(self, stream):
        self.serialize(stream)
