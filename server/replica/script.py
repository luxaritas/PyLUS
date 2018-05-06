"""
Script component
"""

from pyraknet.bitstream import c_bit

from replica.component import Component


class Script(Component):
    """
    Script component class
    """
    def write_construction(self, stream):
        stream.write(c_bit(False))  # TODO: add a var for this

    def serialize(self, stream):
        pass
