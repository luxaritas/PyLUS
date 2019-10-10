"""
Inventory component
"""

from bitstream import c_bit, c_uint32

from .component import Component


class Inventory(Component):
    """
    Inventory component class
    """
    def __init__(self, items = []):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_construction(self, stream):
        self.serialize(stream)

    def serialize(self, stream):
        stream.write(c_bit(True))
        stream.write(c_uint32(0))  # TODO: add items

        stream.write(c_bit(True))  # NOTE: unknown
        stream.write(c_uint32(0))  # NOTE: unknown
