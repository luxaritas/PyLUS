"""
Packet router
"""

import logging

from pyraknet.bitstream import ReadStream
from server.plugin import Plugin, Action, Packet
from server.structs import LUHeader


log = logging.getLogger(__name__)


class PacketRouter(Plugin):
    """
    Packet router plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('rn:user_packet', self.on_packet, 10)
        ]

    def on_packet(self, data, address):
        """
        Packet handler
        """
        packet = Packet.deserialize(ReadStream(data), self.server.packets)

        if not getattr(packet.header, 'packet_name', None):
            self.server.handle('pkt:unknown_packet', packet)
        else:
            log.debug(f'[{self.server.type}] Recieved LU Packet {packet.header.packet_name}')
            self.server.handle(f'pkt:{packet.header.packet_name}', packet, address)
