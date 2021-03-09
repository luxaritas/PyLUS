"""
World manager
"""

from bitstream import ReadStream, WriteStream, c_uint16, c_int64, c_bool
from pyraknet.transports.abc import Connection

from server.plugin import Plugin, Action
from server.structs import Packet, CString
from server.enums import ZONE_NAMES

class WorldRedirect(Plugin):
    """
    World manager class
    """

    def actions(self):
        """
        Returns list of actions
        """
        return [
            Action('pkt:join_world_request', self.join_world_request, 10),
        ]

    def packets(self):
        """
        Returns list of packets
        """
        return [
            JoinWorldRequest,
        ]

    def join_world_request(self, packet: 'JoinWorldRequest', conn: Connection):
        """
        Handles initial redirect from char list
        """
        session = self.server.handle_until_return('session:get_session', conn.get_address())
        # One of the plugins listening is expected to set session.character
        self.server.handle('session:char_selected', session, packet.character_id)

        last_zone = self.server.handle_until_return('char:initial_zone', session.character)
        zone_conf = self.server.config.servers.to_dict()[ZONE_NAMES[last_zone]]

        res = RedirectToServer(zone_conf['public_host'], zone_conf['public_port'])
        conn.send(res)

class JoinWorldRequest(Packet):
    """
    Join world request packet
    """
    packet_name = 'join_world_request'

    def __init__(self, character_id):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    @classmethod
    def deserialize(cls, stream: ReadStream):
        """
        Deserializes the packet
        """
        char_id = stream.read(c_int64)
        return cls(char_id)

class RedirectToServer(Packet):
    """
    Redirects client to a new server instance
    """
    packet_name = 'redirect_to_server'

    def __init__(self, ip, port, mythran_notification=False):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream: WriteStream):
        super().serialize(stream)
        stream.write(CString(self.ip, allocated_length=33))
        stream.write(c_uint16(self.port))
        stream.write(c_bool(self.mythran_notification))
