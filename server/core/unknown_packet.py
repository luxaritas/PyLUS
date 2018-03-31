from plugin import Plugin, Action
import logging
log = logging.getLogger(__name__)

class UnknownHandler(Plugin):
    def actions(self):
        return [
            Action('pkt:unknown_packet', self.log_unknown, 10)
        ]
    
    def log_unknown(self, packet):
        log.info('[{}] Recieved unknown packet with remote connection ID {} and packet ID {}: {}'.format(
            self.server.type, packet.header.remote_conn_id, packet.header.packet_id, packet.data.hex()
        ))