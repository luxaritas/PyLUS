"""
Stats component
"""

from pyraknet.bitstream import c_bit, c_uint32, c_float, c_int32

from replica.component import Component


class Stats(Component):
    """
    Stats component class
    """
    def __init__(self, stats=True, health=100, max_health=100, armor=0, max_armor=100, imagination=0,
                 max_imagination=100, factions=[], smashable=False):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_construction(self, stream):
        stream.write(c_bit(True))  # NOTE: unknown
        for _ in range(9):
            stream.write(c_uint32(0))

        self.write_data(stream)

        if self.stats:
            stream.write(c_bit(False))  # NOTE: unknown(?)
            stream.write(c_bit(False))  # NOTE: same as above

            if self.smashable:
                stream.write(c_bit(False))  # NOTE: unknown
                stream.write(c_bit(False))  # NOTE: same as above

        stream.write(c_bit(False))

    def serialize(self, stream):
        self.write_data(stream)
        stream.write(c_bit(False))  # NOTE: unknown flag

    def write_data(self, stream):
        stream.write(c_bit(self.stats))

        if self.stats:
            stream.write(c_uint32(self.health))
            stream.write(c_float(self.max_health))

            stream.write(c_uint32(self.armor))
            stream.write(c_float(self.max_armor))

            stream.write(c_uint32(self.imagination))
            stream.write(c_float(self.max_imagination))

            stream.write(c_uint32(0))  # NOTE: unknown
            stream.write(c_bit(False))
            stream.write(c_bit(False))
            stream.write(c_bit(False))

            stream.write(c_float(self.max_health))
            stream.write(c_float(self.max_armor))
            stream.write(c_float(self.max_imagination))

            stream.write(c_uint32(len(self.factions)))

            for faction_id in self.factions:
                stream.write(c_int32(faction_id))

            stream.write(c_bit(self.smashable))
