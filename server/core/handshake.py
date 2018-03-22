from pyraknet.bitstream import WriteStream, c_uint16, c_uint32
from plugin import Plugin
from structs import LUHeader

class Handshake(Plugin):
    def actions(self):
        return {
            'pkt:handshake': (self.handshake, 10)
        }
    
    def handshake(self, data, address):
        game_version = data.read(c_uint32)
        unknown = data.read(c_uint32)
        remote_conn_type = data.read(c_uint32)
        client_pid = data.read(c_uint32)
        local_port = data.read(c_uint16)
        local_ip = data.read(bytes, allocated_length=33)
        
        res = WriteStream()
        # Packet
        res.write(LUHeader('handshake'))
        # Version
        res.write(c_uint32(171022))
        # Unknown
        res.write(c_uint32(0x93))
        # Remote connection type
        res.write(c_uint32(0x01 if self.server.type == 'auth' else 0x04))
        # Process ID (we won't expose this)
        res.write(c_uint32(0))
        # Local port
        res.write(c_uint16(0xff))
        # Local IP
        res.write(b'127.0.0.1', allocated_length=33)
        self.server.rnserver.send(res, address)