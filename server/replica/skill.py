"""
Skill component
"""

from pyraknet.bitstream import c_bit

from .component import Component


class Skill(Component):
    """
    Skill component class
    """
    def write_construction(self, stream):
        stream.write(c_bit(False))  # TODO: add a var for this

    def serialize(self, stream):
        pass
