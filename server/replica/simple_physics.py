"""
SimplePhysics component
"""

from pyraknet.bitstream import c_bit, c_float

from .component import Component

from server.structs import Vector3, Vector4


class SimplePhysics(Component):
    """
    SimplePhysics component class
    """
    def __init__(self, pos=Vector3(0, 0, 0), rot=Vector4(0, 0, 0, 0)):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_construction(self, stream):
        """
        Writes construction data to a stream
        """
        stream.write(c_bit(False))  # NOTE: unknown
        stream.write(c_float(0))  # NOTE: unknown

        self.serialize(stream)

    def serialize(self, stream):
        """
        Serializes the component
        """
        stream.write(c_bit(False))  # NOTE: unknown
        stream.write(c_bit(False))  # NOTE: unknown

        stream.write(c_bit(True))
        stream.write(c_float(self.pos.x))
        stream.write(c_float(self.pos.y))
        stream.write(c_float(self.pos.z))
        stream.write(c_float(self.rot.x))
        stream.write(c_float(self.rot.y))
        stream.write(c_float(self.rot.z))
        stream.write(c_float(self.rot.w))
