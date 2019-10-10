"""
Session manager
"""

import bcrypt

from datetime import datetime, timedelta

from bitstream import c_byte, c_ubyte, ReadStream
from pyraknet.transports.abc import Connection
from django.utils.timezone import now

from cms.game.models import Session, Account, Character
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
            Action('pkt:session_info', self.verify_session, 10),
            Action('rn:user_packet', self.allow_packet, 10),
            Action('session:get_session', self.get_session, 10),
            Action('session:char_selected', self.set_char, 10)
        ]

    def packets(self):
        """
        Returns all packets
        """
        return [
            SessionInfo
        ]

    def verify_session(self, packet: 'SessionInfo', conn: Connection):
        """
        Verifies a session
        """
        try:
            session = Session.objects.get(account__user__username=packet.username)
            self.session_cache[conn.get_address()] = session
        except Session.DoesNotExist:
            session = None

        if not session or \
           not bcrypt.checkpw(packet.session_key.encode('latin1'), session.token) or \
               now() - session.created > timedelta(days=1):
            self.destroy_session(conn)
        else:
            # Client address may change when switching servers
            session.ip = conn.get_address()[0]
            session.port = conn.get_address()[1]
            session.save()
            self.server.handle('session:verify_success', session, conn)

    def allow_packet(self, data: ReadStream, conn: Connection):
        """
        Allows a packet
        """
        packet = Packet.deserialize(ReadStream(data), self.server.packets)

        if not getattr(packet, 'allow_without_session') and not self.get_session(conn.get_address()):
            self.destroy_session(conn)

    def get_session(self, address):
        """
        Returns a user session
        """
        return self.session_cache.get(address)

    def destroy_session(self, conn: Connection):
        """
        Destroys a session
        """
        address = conn.get_address()
        Session.objects.filter(ip=address[0], port=address[1]).delete()
        conn.close()
        
    def set_char(self, session, char_id):
        """
        Records the selected char for the given session
        """
        session.character = session.account.character_set.get(pk=char_id)
        session.save()


class SessionInfo(Packet):
    """
    Session info packet
    """
    packet_name = 'session_info'
    allow_without_session = True

    @classmethod
    def deserialize(cls, stream: ReadStream):
        """
        Deserializes the packet
        """
        return cls(username=stream.read(str, allocated_length=33),
                   session_key=stream.read(str, allocated_length=33),
                   unknown=stream.read(bytes, length=33))
