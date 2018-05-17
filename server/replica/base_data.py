"""
Base data
"""

from pyraknet.bitstream import c_uint8, c_uint32, c_int32, c_int64, c_float, c_bit
from pyraknet.replicamanager import Replica


class BaseData(Replica):
    """
    Base data class
    """

    def __init__(self, objid, lot, name, time_since_created=0, trigger=False, spawner=None, spawner_node=None, scale=None, components=[]):
        self.objid = objid
        self.lot = lot
        self.name = name
        self.time_since_created = time_since_created
        self.trigger = trigger
        self.spawner_node = spawner_node
        self.spawner = spawner
        self.scale = scale
        self.components = components

    def write_construction(self, stream):
        stream.write(c_int64(self.objid))
        stream.write(c_int32(self.lot))
        stream.write(self.name, length_type=c_uint8)
        stream.write(c_uint32(self.time_since_created))
        stream.write(c_bit(False))  # TODO: add var for this
        stream.write(c_bit(self.trigger))

        stream.write(c_bit(self.spawner != None))
        if self.spawner:
            stream.write(c_int64(self.spawner))

        stream.write(c_bit(self.spawner_node != None))
        if self.spawner_node:
            stream.write(c_uint32(self.spawner_node))

        stream.write(c_bit(self.scale != None))
        if self.scale:
            stream.write(c_float(self.scale))

        stream.write(c_bit(False))
        stream.write(c_bit(False))

        stream.write(c_bit(True))
        stream.write(c_bit(False))
        stream.write(c_bit(False))

        for component in self.components:
            component.write_construction(stream)

    def serialize(self, stream):
        stream.write(c_bit(True))
        stream.write(c_bit(False))
        stream.write(c_bit(False))

        for component in self.components:
            component.serialize(stream)
