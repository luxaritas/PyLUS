"""
Packets
"""

from pyraknet.bitstream import c_int64, c_uint16

from plugin import Packet


class GameMessage(Packet):
    """
    Game message packet
    """
    packet_name = 'server_game_message'

    def __init__(self, objid, message_id, data=None):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        super().serialize(stream)

        stream.write(c_int64(self.objid))
        stream.write(c_uint16(self.message_id))

        if getattr(self, 'data', None):
            if isinstance(self.data, bytes):
                stream.write(self.data)
            else:
                stream.write(bytes(self.data))
