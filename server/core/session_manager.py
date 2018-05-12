"""
Session manager
"""

import secrets
import bcrypt

from pyraknet.bitstream import c_byte, c_ubyte, ReadStream

from plugin import Plugin, Action, Packet


class SessionManager(Plugin):
    """
    Session manager plugin
    """
    sessions = {}

    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('session:new_session', self.new_session, 10),
            Action('session:get_session', self.get_session, 10),
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

    def new_session(self, address, uid):
        """
        Creates a new session
        """
        token = secrets.token_urlsafe(24)
        hashed = bcrypt.hashpw(token.encode('latin1'), bcrypt.gensalt())

        self.sessions[address] = Session(uid, hashed)

        return token

    def get_session(self, address):
        """
        Returns a user id
        """
        return self.sessions.get(address)

    def verify_session(self, packet, address):
        """
        Verifies a session
        """
        if address not in self.sessions or not self.sessions[address].check_token(packet.session_key):
            self.server.rnserver.close_connection(address)

        # if not self.server.handle_until_value('auth:check_token', True, packet.username, packet.session_key):
        #     self.server.rnserver.close_connection(address)

    def allow_packet(self, data, address):
        """
        Allows a packet
        """
        packet = Packet.deserialize(ReadStream(data), self.server.packets)

        if not getattr(packet, 'allow_without_session') and address not in self.sessions:
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
                   unknown=stream.read(bytes, allocated_length=33))

class Session:
    """
    User session class
    """
    def __init__(self, uid, token):
        self.uid = uid
        self.token = token
        self.objid = None
        self.clone = None
        self.instance = None

    def check_token(self, token):
        return bcrypt.checkpw(token.encode('latin1'), self.token)
