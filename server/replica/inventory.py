"""
Inventory component
"""

from pyraknet.bitstream import c_bit

from replica.component import Component


class Inventory(Component):
    """
    Inventory component class
    """
    def write_construction(self, stream):
        self.serialize(stream)

    def serialize(self, stream):
        stream.write(c_bit(False))  # TODO: add a var for this

        stream.write(c_bit(False))  # NOTE: unknown
