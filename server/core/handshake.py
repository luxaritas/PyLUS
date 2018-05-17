"""
Handshake
"""

from pyraknet.bitstream import c_uint16, c_uint32
from server.plugin import Plugin, Action, Packet


class Handshake(Plugin):
    """
    Handshake plugin
    """
    def __init__(self, server):
        super().__init__(server)

    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('pkt:handshake', self.handshake, 10),
        ]

    def packets(self):
        """
        Returns all packets
        """
        return [
            HandshakePacket,
        ]

    def handshake(self, packet, address):
        """
        Makes a handshake with a client
        """
        remote_conn_type = 0x01 if self.server.type == 'auth' else 0x04
        self.server.rnserver.send(HandshakePacket(remote_conn_type), address)


class HandshakePacket(Packet):
    """
    Handshake packet
    """
    packet_name = 'handshake'
    allow_without_session = True

    def __init__(self, remote_conn_type, game_version=171022, unknown=0x93, process_id=0, local_port=0xff,
                 local_ip=b'127.0.0.1'):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)
        stream.write(c_uint32(self.game_version))
        stream.write(c_uint32(self.unknown))
        stream.write(c_uint32(self.remote_conn_type))
        stream.write(c_uint32(self.process_id))
        stream.write(self.local_ip, allocated_length=33)

    @classmethod
    def deserialize(cls, stream):
        """
        Deserializes the packet
        """
        return cls(game_version=stream.read(c_uint32),
                   unknown=stream.read(c_uint32),
                   remote_conn_type=stream.read(c_uint32),
                   process_id=stream.read(c_uint32),
                   local_port=stream.read(c_uint16),
                   local_ip=stream.read(bytes, allocated_length=33))
