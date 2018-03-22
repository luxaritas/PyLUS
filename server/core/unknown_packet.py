from plugin import Plugin
import logging
log = logging.getLogger(__name__)

class UnknownHandler(Plugin):
    def actions(self):
        return {
            'pkt:unknown_packet': (self.log_unknown, 10)
        }
    
    def log_unknown(self, remote_conn_id, packet_id, data):
        log.info('Recieved unknown packet with remote connection ID {} and packet ID {}'.format(remote_conn_id, packet_id))