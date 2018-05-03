from pyraknet import c_byte
from plugin import Plugin, Action, Packet
from structs import CString

class SessionVerification(Plugin):
    def actions(self):
        return [
            Action('pkt:session_info', self.verify_session, 10),
            Action('rn:user_packet', self.allow_packet, 10),
        ]
    
    def packets(self):
        return [
            SessionInfo
        ]
    
    def verify_session(self, packet, address):
        if self.server.handle_until_value('auth:check_token', True, packet.username, packet.session_key):
            self.server.connections[address]['valid_session'] = True
        else:
            self.server.rnserver.close_connection(address)
            
    def allow_packet(self, data, address):
        packet = Packet.deserialize(ReadStream(data), self.server.packets)
        
        if not getattr(packet, 'allow_without_session'):
            conn = self.server.connections.get(address, None)
            if conn is None or conn.get('valid_session') is not True:
                self.server.rnserver.close_connection(address) 
        

class SessionInfo(Packet):
    @classmethod
    def deserialize(cls, stream):
        return cls(
            username = stream.read(str, allocated_length=33),
            session_key = stream.read(str, allocated_length=33),
            unknown = stream.read(CString(allocated_length=32)),
            unknown1 = stream.read(c_byte)
        )
    