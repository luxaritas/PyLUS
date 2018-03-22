from pyraknet.bitstream import Serializable, c_uint8, c_uint16, c_uint32
from enums import PACKET_IDS, PACKET_NAMES

class LUHeader(Serializable):
    def __init__(self, packet_name=None, remote_conn_type=None, packet_id=None):
        if packet_name is None and (remote_conn_type is None or packet_id is None):
            raise ValueError('LUHeader requires either a packet name or a remote connection type and packet ID')
        
        self.packet_name = packet_name
        self.raw_ids = (remote_conn_type, packet_id)
    
    @property
    def remote_conn_type(self):
        if self.packet_name is not None:
            return PACKET_IDS[self.packet_name][0]
        return self.raw_ids[0]
    
    @property
    def packet_id(self):
        if self.packet_name is not None:
            return PACKET_IDS[self.packet_name][1]
        return self.raw_ids[1]
    
    def serialize(self, stream: "WriteStream") -> None:
        stream.write(c_uint8(0x53))
        stream.write(c_uint16(self.remote_conn_type))
        stream.write(c_uint32(self.packet_id))
        stream.write(c_uint8(0x00))
      
    @classmethod
    def deserialize(cls, stream: "ReadStream") -> 'LUHeader':
        """Create a new object from the bitstream."""
        rntype = stream.read(c_uint8)
        remote_conn_type = stream.read(c_uint16)
        packet_id = stream.read(c_uint32)
        unknown = stream.read(c_uint8)
        
        packet_name = PACKET_NAMES.get(remote_conn_type, {}).get(packet_id, None)
        
        return cls(packet_name, remote_conn_type, packet_id)
      