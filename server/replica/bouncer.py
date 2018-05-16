"""
Bouncer component
"""

from pyraknet.bitstream import c_bit

from replica.component import Component


class Bouncer(Component):
    """
    Bouncer component class
    """
    def __init__(self, requires_pet=False):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_construction(self, stream):
        self.serialize(stream)

    def serialize(self, stream):
        stream.write(c_bit(True))
        stream.write(c_bit(not self.requires_pet))
