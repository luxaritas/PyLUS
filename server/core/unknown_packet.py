"""
Unknown packet
"""

import logging

from server.plugin import Plugin, Action
from server.structs import Packet

log = logging.getLogger(__name__)


class UnknownHandler(Plugin):
    """
    Unknown packet handler plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('pkt:unknown_packet', self.log_unknown, 10)
        ]

    def log_unknown(self, packet: Packet):
        """
        Logs an unknown packet
        """
        server_type = self.server.type
        remote_conn_id = packet.header.remote_conn_id
        packet_id = packet.header.packet_id
        data_hex = packet.data.hex()

        log.info(f'[{server_type}] Recieved unknown packet with remote connection ID {remote_conn_id} ' \
                 f'and packet ID {packet_id}: {data_hex}')
