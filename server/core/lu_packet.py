import logging
from pyraknet.bitstream import c_uint8, c_uint16, c_uint32, ReadStream
from plugin import Plugin
from structs import LUHeader

log = logging.getLogger(__name__)

class PacketRouter(Plugin):
    def actions(self):
        return {
            'rn:user_packet': (self.on_packet, 10)
        }
    
    def on_packet(self, data, address):
        stream = ReadStream(data)
        header = LUHeader.deserialize(stream)
        packet = stream.read_remaining()
        
        if header.packet_name == None:
            self.server.handle('lu:unknown_packet', header.remote_conn_type, header.packet_id, ReadStream(packet))
        else:
            log.debug('Recieved LU Packet {}'.format(header.packet_name))
            self.server.handle('pkt:' + header.packet_name, ReadStream(packet), address)
            