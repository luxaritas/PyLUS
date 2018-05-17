"""
Script component
"""

from pyraknet.bitstream import c_bit

from replica.component import Component


class Script(Component):
    """
    Script component class
    """
    def __init__(self, script=False):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_construction(self, stream):
        stream.write(c_bit(self.script))

    def serialize(self, stream):
        pass
