"""
Player object
"""

from pyraknet.bitstream import c_uint8, c_uint32, c_int32, c_int64, c_float, c_bit
from pyraknet.replicamanager import Replica

from replica.controllable_physics import ControllablePhysics
from replica.character import Character
from replica.render import Render

from structs import WString

class Player(Replica):
    """
    Player replica object
    """
    def __init__(self, name):
        self.name = name
        self.control = ControllablePhysics(player=True)
        self.char = Character()
        self.render = Render()

    def serialize(self, stream):
        stream.write(c_bit(False))

        self.control.serialize(stream)
        self.char.serialize(stream)
        self.render.serialize(stream)

    def write_construction(self, stream):
        stream.write(c_int64(9999999999))
        stream.write(c_int32(0))

        stream.write(c_uint8(len(self.name)))
        stream.write(WString(self.name, length=16))

        stream.write(c_bit(False))
        stream.write(c_bit(False))
        stream.write(c_bit(False))
        stream.write(c_bit(False))
        stream.write(c_bit(False))
        stream.write(c_bit(False))
        stream.write(c_bit(False))

        stream.write(c_bit(False))

        self.control.write_construction(stream)
        self.char.write_construction(stream)
        self.render.write_construction(stream)
