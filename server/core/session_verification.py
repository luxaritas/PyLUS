"""
Session verification
"""

from pyraknet.bitstream import c_byte, ReadStream

from plugin import Plugin, Action, Packet
from structs import CString


class SessionVerification(Plugin):
    """
    Session verification plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('pkt:session_info', self.verify_session, 10),
            Action('rn:user_packet', self.allow_packet, 10),
        ]

    def packets(self):
        """
        Returns all packets
        """
        return [
            SessionInfo
        ]

    def verify_session(self, packet, address):
        """
        Verifies a session
        """
        if self.server.handle_until_value('auth:check_token', True, packet.username, packet.session_key):
            self.server.connections[address]['uid'] = self.server.handle_until_value('auth:get_user_id', True, address)
        else:
            self.server.rnserver.close_connection(address)

    def allow_packet(self, data, address):
        """
        Allows a packet
        """
        packet = Packet.deserialize(ReadStream(data), self.server.packets)

        if not getattr(packet, 'allow_without_session'):
            conn = self.server.connections.get(address)
            if not conn or not conn.get('username'):
                self.server.rnserver.close_connection(address)


class SessionInfo(Packet):
    """
    Session info packet
    """
    packet_name = 'session_info'
    allow_without_session = True

    @classmethod
    def deserialize(cls, stream):
        """
        Deserializes the packet
        """
        return cls(username=stream.read(str, allocated_length=33),
                   session_key=stream.read(str, allocated_length=33),
                   unknown=stream.read(CString(allocated_length=32)),
                   unknown1=stream.read(c_byte))
