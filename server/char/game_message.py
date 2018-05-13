"""
Game message handling
"""

from pyraknet.bitstream import ReadStream, WriteStream, c_int64, c_int, c_bit, c_uint32

from enums import GameMessageID
from structs import ClientGameMessage, ServerGameMessage
from plugin import Action, Plugin


class GameMessageHandler(Plugin):
    """
    Game message handler
    """
    def actions(self):
        """
        Returns the actions for the game message handler
        """
        return [
            Action('pkt:client_game_message', self.client_game_message, 10),
        ]

    def packets(self):
        """
        Returns the packets for the game message handler
        """
        return [
            ClientGameMessage
        ]

    def client_game_message(self, packet, address):
        """
        Handles the game messages
        """

        if packet.message_id == GameMessageID.REQUEST_USE:
            stream = ReadStream(packet.extra_data)

            self.request_use(packet, address, stream)
        elif packet.message_id == GameMessageID.MISSION_DIALOGUE_OK:
            stream = ReadStream(packet.extra_data)

            self.mission_accept(packet, address, stream)
        elif packet.message_id == 888:
            pass
        else:
            print(f'Unhandled game message: {packet.message_id}')

    def request_use(self, packet, address, stream):
        """
        Handles the request use game message
        """
        session = self.server.handle_until_return('session:get_session', address)
        clone = self.server.handle_until_return('world:get_clone', session.clone)

        multiinteract = stream.read(c_bit)
        multiinteract_id = stream.read(c_uint32)
        multiinteract_type = stream.read(c_int)
        objid = stream.read(c_int64)
        secondary = stream.read(c_bit)

        print(f'Multi interact: {multiinteract}')
        print(f'Multi interact ID: {multiinteract_id}')
        print(f'Multi interact type: {multiinteract_type}')
        print(f'Object ID: {objid}')
        print(f'Secondary: {secondary}')

        obj = [x for x in clone.objects if x.objid == objid][0]

        if obj.lot == 14349:
            msg = ServerGameMessage(packet.objid, GameMessageID.OFFER_MISSION, c_int(1727) + c_int64(objid))

            self.server.rnserver.send(msg, address)

    def mission_accept(self, packet, address, stream):
        """
        Handles the mission dialogue ok game message
        """
        complete = stream.read(c_bit)
        state = stream.read(c_int)
        mission_id = stream.read(c_int)
        responder_objid = stream.read(c_int64)

        print(f'Mission {mission_id} accepted')
        print(f'Complete: {complete}')
        print(f'State: {state}')
        print(f'Responder: {responder_objid}')

        wstream = WriteStream()
        wstream.write(c_int(mission_id))
        wstream.write(c_int(state))
        wstream.write(c_bit(False))
        wstream.write(c_bit(False))

        msg = ServerGameMessage(packet.objid, GameMessageID.NOTIFY_MISSION, wstream)
        self.server.rnserver.send(msg, address)
