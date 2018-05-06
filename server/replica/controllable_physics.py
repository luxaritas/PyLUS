"""
Controllable physics
"""

from pyraknet.bitstream import c_bit, c_uint32, c_float, c_int64
from pyraknet.replicamanager import Replica

from replica.component import Component


class ControllablePhysics(Component):
    """
    Controllable physics component
    """

    def __init__(self, jetpack=False, jetpack_effect=0, player=False, player_x=0, player_y=1, player_z=0, player_rot_x=0,
                 player_rot_y=0, player_rot_z=0, player_rot_w=0, player_ground=True, player_rail=False, player_velocity=False, player_velocity_x=0,
                 player_velocity_y=0, player_velocity_z=0, player_angular_velocity=False, player_angular_velocity_x=0,
                 player_angular_velocity_y=0, player_angular_velocity_z=0, player_platform=False):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_data(self, stream):
        """
        Writes object data
        """
        stream.write(c_bit(False))  # NOTE: flag is unknown
        stream.write(c_bit(False))  # NOTE: same as above
        stream.write(c_bit(False))  # NOTE: same here

        stream.write(c_bit(self.player))

        if self.player:
            stream.write(c_float(self.player_x))
            stream.write(c_float(self.player_y))
            stream.write(c_float(self.player_z))

            stream.write(c_float(self.player_rot_x))
            stream.write(c_float(self.player_rot_y))
            stream.write(c_float(self.player_rot_z))
            stream.write(c_float(self.player_rot_w))

            stream.write(c_bit(self.player_ground))
            stream.write(c_bit(self.player_rail))

            stream.write(c_bit(self.player_velocity))

            if self.player_velocity:
                stream.write(c_float(self.player_velocity_x))
                stream.write(c_float(self.player_velocity_y))
                stream.write(c_float(self.player_velocity_z))

            stream.write(c_bit(self.player_angular_velocity))

            if self.player_angular_velocity:
                stream.write(c_float(self.player_angular_velocity_x))
                stream.write(c_float(self.player_angular_velocity_y))
                stream.write(c_float(self.player.angular_velocity_z))

            stream.write(c_bit(False))  # NOTE: unknown flag

    def write_construction(self, stream):
        stream.write(c_bit(self.jetpack))

        if self.jetpack:
            stream.write(c_uint32(self.jetpack_effect))
            stream.write(c_bit(False))

        stream.write(c_bit(False))  # NOTE: flag is unknown

        self.write_data(stream)

    def serialize(self, stream):
        self.write_data(stream)

        stream.write(c_bit(True))  # NOTE: should this be true?
