import logging
from pyraknet.bitstream import c_uint8, c_uint16, c_uint32, ReadStream
from plugin import Plugin, Action, Packet
from structs import LUHeader

log = logging.getLogger(__name__)

class PacketRouter(Plugin):
    def actions(self):
        return [
            Action('rn:user_packet', self.on_packet, 10)
        ]
    
    def on_packet(self, data, address):
        packet = Packet.deserialize(ReadStream(data), self.server.packets)
        
        if getattr(packet.header,'packet_name', None) is None:
            self.server.handle('pkt:unknown_packet', packet)
        else:
            log.debug(f'[{self.server.type}] Recieved LU Packet {packet.header.packet_name}'
            self.server.handle(f'pkt:{packet.header.packet_name}', packet, address)
            