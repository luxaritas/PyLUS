"""
Session verification
"""

from pyraknet.bitstream import c_byte, c_ubyte, ReadStream

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
        pass

        # TODO: fix token checking
        # if not self.server.handle_until_value('auth:check_token', True, packet.username, packet.session_key):
        #     self.server.rnserver.close_connection(address)

    def allow_packet(self, data, address):
        """
        Allows a packet
        """
        packet = Packet.deserialize(ReadStream(data), self.server.packets)

        if not getattr(packet, 'allow_without_session'):
            uid = self.server.handle_until_return('auth:get_user_id', address)
            if not uid:
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
                   # unknown=stream.read(CString('', allocated_length=32)),
                   unknown=stream.read(c_ubyte, allocated_length=16),  # NOTE: this seems to work, while reading a CString doesn't
                   unknown1=stream.read(c_byte))
