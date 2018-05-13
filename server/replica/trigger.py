"""
Trigger component
"""

from pyraknet.bitstream import c_bit, c_int32

from replica.component import Component


class Trigger(Component):
    """
    Trigger component class
    """
    def __init__(self, trigger_id=None):
        self.trigger_id = trigger_id

    def write_construction(self, stream):
        """
        Writes construction data
        """
        self.serialize(stream)

    def serialize(self, stream):
        """
        Serializes the component
        """
        stream.write(c_bit(self.trigger_id != None))
        if self.trigger_id:
            stream.write(c_int32(self.trigger_id))
