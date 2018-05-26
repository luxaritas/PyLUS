"""
Session manager
"""

import secrets
import bcrypt
from datetime import datetime, timedelta

from pyraknet.bitstream import c_byte, c_ubyte, ReadStream

from cms.game.models import Session, Account
from server.plugin import Plugin, Action, Packet


class SessionManager(Plugin):
    """
    Session manager plugin
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.session_cache = {}

    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('session:new_session', self.new_session, 10),
            Action('pkt:session_info', self.verify_session, 10),
            Action('rn:user_packet', self.allow_packet, 10),
            Action('session:get_session', self.get_session, 10),
            Action('session:set_clone', self.set_clone, 10),
        ]

    def packets(self):
        """
        Returns all packets
        """
        return [
            SessionInfo
        ]

    def new_session(self, account, address):
        """
        Creates a new session
        """
        token = secrets.token_urlsafe(24)
        hashed = bcrypt.hashpw(token, bcrypt.gensalt())

        session = Session(account=account, ip=address[0], port=address[1], token=hashed)
        session.save()

        return token

    def verify_session(self, packet, address):
        """
        Verifies a session
        """
        try:
            session = Session.objects.get(ip=address[0], port=address[1])
            self.session_cache[address] = session
        except Session.DoesNotExist:
            session = None

        if not session or \
           not bcrypt.checkpw(packet.session_key, session.token) or \
               datetime.utcnow() - session.created > timedelta(days=1):
            self.destroy_session(address)

    def allow_packet(self, data, address):
        """
        Allows a packet
        """
        packet = Packet.deserialize(ReadStream(data), self.server.packets)

        if not getattr(packet, 'allow_without_session') and not self.get_session(address):
            self.destroy_session(address)

    def get_session(self, address):
        """
        Returns a user session
        """
        return self.session_cache.get(address)

    def destroy_session(self, address):
        """
        Destroys a session
        """
        Session.objects.filter(ip=address[0], port=address[1]).delete()
        self.server.rnserver.close_connection(address)

    def set_clone(self, address, clone):
        """
        Sets the world clone for a session
        """
        session = Session.objects.get(ip=address[0], port=address[1])
        session.clone = clone
        session.save()


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
