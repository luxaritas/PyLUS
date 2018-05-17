"""
Rebuild component
"""

from pyraknet.bitstream import c_bit, c_uint32, c_float

from .component import Component
from server.structs import Vector3


class Rebuild(Component):
    """
    Rebuild component class
    """
    def __init__(self, state=0, success=False, enabled=True, start=0, paused=0, activator_pos=Vector3(0, 0, 0)):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_construction(self, stream):
        self.serialize(stream)

        stream.write(c_bit(False))

        stream.write(c_float(self.activator_pos.x))
        stream.write(c_float(self.activator_pos.y))
        stream.write(c_float(self.activator_pos.z))

        stream.write(c_bit(True))

    def serialize(self, stream):
        stream.write(c_bit(True))
        stream.write(c_uint32(0))

        stream.write(c_bit(True))
        stream.write(c_uint32(self.state))
        stream.write(c_bit(self.success))
        stream.write(c_bit(self.enabled))
        stream.write(c_float(self.start))
        stream.write(c_float(self.paused))
