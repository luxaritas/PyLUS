"""
Controllable physics
"""

from bitstream import c_bit, c_uint32, c_float, c_int64
from pyraknet.replicamanager import Replica

from .component import Component
from server.structs import Vector3, Vector4


class ControllablePhysics(Component):
    """
    Controllable physics component
    """

    def __init__(self, jetpack=False, jetpack_effect=0, player=True, player_pos=Vector3(0, 0, 0), player_rot=Vector4(0, 0, 0, 0),
                 player_ground=True, player_rail=False, player_velocity=False, player_velocity_vec=Vector3(0, 0, 0),
                 player_angular_velocity=False, player_angular_velocity_vec=Vector3(0, 0, 0), player_platform=False):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_data(self, stream):
        """
        Writes object data
        """
        stream.write(c_bit(False))  # NOTE: flag is unknown

        stream.write(c_bit(True))  # NOTE: same as above
        stream.write(c_float(0))
        stream.write(c_bit(False))

        stream.write(c_bit(True))  # NOTE: same here
        stream.write(c_bit(False))

        stream.write(c_bit(self.player))

        if self.player:
            stream.write(c_float(self.player_pos.x))
            stream.write(c_float(self.player_pos.y))
            stream.write(c_float(self.player_pos.z))

            stream.write(c_float(self.player_rot.x))
            stream.write(c_float(self.player_rot.y))
            stream.write(c_float(self.player_rot.z))
            stream.write(c_float(self.player_rot.w))

            stream.write(c_bit(self.player_ground))
            stream.write(c_bit(self.player_rail))

            stream.write(c_bit(self.player_velocity))

            if self.player_velocity:
                stream.write(c_float(self.player_velocity_vec.x))
                stream.write(c_float(self.player_velocity_vec.y))
                stream.write(c_float(self.player_velocity_vec.z))

            stream.write(c_bit(self.player_angular_velocity))

            if self.player_angular_velocity:
                stream.write(c_float(self.player_angular_velocity_vec.x))
                stream.write(c_float(self.player_angular_velocity_vec.y))
                stream.write(c_float(self.player.angular_velocity_vec.z))

            stream.write(c_bit(False))  # NOTE: unknown flag

    def write_construction(self, stream):
        stream.write(c_bit(self.jetpack))

        if self.jetpack:
            stream.write(c_uint32(self.jetpack_effect))
            stream.write(c_bit(False))

        stream.write(c_bit(True))  # NOTE: flag is unknown

        for _ in range(7):
            stream.write(c_uint32(0))

        self.write_data(stream)

    def serialize(self, stream):
        self.write_data(stream)

        stream.write(c_bit(False))  # NOTE: should this be true?
