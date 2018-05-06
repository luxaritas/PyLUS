"""
Render component
"""

from pyraknet.bitstream import c_uint32
from pyraknet.replicamanager import Replica

from replica.component import Component


class Render(Component):
    """
    Render component replica
    """
    def write_construction(self, stream):
        stream.write(c_uint32(0))  # TODO: add a var for this

    def serialize(self, stream):
        pass
