"""
PhantomPhysics component
"""

from pyraknet.bitstream import c_bit, c_float, c_uint32

from replica.component import Component
from structs import Vector3, Vector4


class PhantomPhysics(Component):
    """
    PhantomPhysics component class
    """

    def __init__(self, pos=Vector3(0, 0, 0), rot=Vector4(0, 0, 0, 0), effect=False, effect_type=0, effect_amount=0,
                 effect_direction=Vector3(0, 0, 0)):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the component
        """
        stream.write(c_bit(True))
        stream.write(c_float(self.pos.x))
        stream.write(c_float(self.pos.y))
        stream.write(c_float(self.pos.z))
        stream.write(c_float(self.rot.x))
        stream.write(c_float(self.rot.y))
        stream.write(c_float(self.rot.z))
        stream.write(c_float(self.rot.w))

        stream.write(c_bit(True))
        stream.write(c_bit(self.effect))
        if self.effect:
            stream.write(c_uint32(self.effect_type))
            stream.write(c_float(self.effect_amount))
            stream.write(c_bit(False))
            stream.write(c_bit(True))
            stream.write(c_float(self.effect_direction.x))
            stream.write(c_float(self.effect_direction.y))
            stream.write(c_float(self.effect_direction.z))

    def write_construction(self, stream):
        """
        Writes construction data
        """
        self.serialize(stream)
