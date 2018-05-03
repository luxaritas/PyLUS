from pyraknet.bitstream import c_uint16, c_uint32
from plugin import Plugin, Action, Packet
from structs import LUHeader

class Handshake(Plugin):
    def __init__(self):
        super().__init__()
        self.server.connections = {}
    
    def actions(self):
        return [
            Action('pkt:handshake', self.handshake, 10),
            Action('rn:disconnect', self.remove_connection, 10)
        ]
    
    def packets(self):
        return [
            HandshakePacket
        ]
    
    def handshake(self, packet, address):
        self.server.connections[address] = {}
        remote_conn_type = 0x01 if self.server.type == 'auth' else 0x04
        self.server.rnserver.send(HandshakePacket(remote_conn_type), address)
        
    def remove_connection(self, address):
        self.server.connections.pop(address)
        
class HandshakePacket(Packet):
    packet_name = 'handshake'
    allow_without_session = True
    
    def __init__(self, remote_conn_type, game_version=171022, unknown=0x93, process_id=0, local_port=0xff, local_ip=b'127.0.0.1'):
        super().__init__(**{k:v for k,v in locals().items() if k != 'self'})
    
    def serialize(self, stream):
        super().serialize(stream)
        stream.write(c_uint32(self.game_version))
        stream.write(c_uint32(self.unknown))
        stream.write(c_uint32(self.remote_conn_type))
        stream.write(c_uint32(self.process_id))
        stream.write(self.local_ip, allocated_length=33)
        
    @classmethod
    def deserialize(cls, stream):
        return cls(
            game_version = stream.read(c_uint32),
            unknown = stream.read(c_uint32),
            remote_conn_type = stream.read(c_uint32),
            process_id = stream.read(c_uint32),
            local_port = stream.read(c_uint16),
            local_ip = stream.read(bytes, allocated_length=33)
        )
        
        