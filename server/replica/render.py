"""
Render component
"""

from pyraknet.bitstream import c_uint32
from pyraknet.replicamanager import Replica

from .component import Component


class Render(Component):
    """
    Render component replica
    """
    def __init__(self, disabled=False):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def write_construction(self, stream):
        """
        Writes construction data
        """
        if not self.disabled:
            stream.write(c_uint32(0))  # TODO: add a var for this

    def serialize(self, stream):
        pass
