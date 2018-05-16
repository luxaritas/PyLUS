"""
Game message handling
"""

from pyraknet.bitstream import ReadStream, WriteStream, c_int64, c_int, c_bit, c_uint32, c_uint8, c_float

from enums import GameMessageID, MissionLockState
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
        if packet.extra_data:
            stream = ReadStream(packet.extra_data)

        if packet.message_id == GameMessageID.REQUEST_USE:
            self.request_use(packet, address, stream)
        elif packet.message_id == GameMessageID.MISSION_DIALOGUE_OK:
            self.mission_accept(packet, address, stream)
        elif packet.message_id == GameMessageID.REQUEST_LINKED_MISSION:
            self.request_linked_mission(packet, address, stream)
        elif packet.message_id == GameMessageID.HAS_BEEN_COLLECTED:
            self.collected(packet, address, stream)
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
        char = self.server.handle_until_return('char:characters', session.account.user.id)[session.account.front_character]
        char_missions = self.server.handle_until_return('char:get_missions', char.id)

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

        objs = [x for x in clone.objects if x.objid == objid]

        if objs:
            obj = objs[0]

            if char_missions:
                missions = self.server.handle_until_return('world:missions_for_lot_target', obj.lot)

                for char_mission in [x for x in char_missions if x.state == 2]:
                    missions2 = [x for x in missions if x[0] == char_mission.mission]

                    if missions2:
                        mission = missions2[0]

                        self.server.handle('char:complete_mission', char.id, mission[0])

                        msg = ServerGameMessage(packet.objid, GameMessageID.OFFER_MISSION, c_int(mission[0]) + c_int64(objid))
                        self.server.rnserver.send(msg, address)

                        return

            missions = self.server.handle_until_return('world:missions_for_lot', obj.lot)
            missions = [x for x in missions if x[0] not in [y.mission for y in char_missions if y.state == 8]]

            if missions:
                mission = missions[0]

                msg = ServerGameMessage(packet.objid, GameMessageID.OFFER_MISSION, c_int(mission[0]) + c_int64(objid))

                self.server.rnserver.send(msg, address)

    def request_linked_mission(self, packet, address, stream):
        """
        Handles the request linked mission game message
        """
        objid = stream.read(c_int64)
        mission = stream.read(c_int)
        offered = stream.read(c_bit)

        print(f'Request for linked mission {mission}')
        print(f'Object ID: {objid}')
        print(f'Offered: {offered}')

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

        session = self.server.handle_until_return('session:get_session', address)
        char = self.server.handle_until_return('char:characters', session.account.user.id)[session.account.front_character]

        if complete:
            self.server.handle('char:complete_mission', char.id, mission_id)

            wstr = WriteStream()
            wstr.write(c_int(mission_id))
            wstr.write(c_int(8))
            wstr.write(c_bit(False))

            msg = ServerGameMessage(responder_objid, GameMessageID.NOTIFY_MISSION, wstr)
        else:

            self.server.handle('char:activate_mission', char.id, mission_id)

            # tasks = self.server.handle_until_return('world:get_mission_tasks', mission_id)

            # for task in tasks:
            #     wstr = WriteStream()
            #     wstr.write(c_int(mission_id))
            #     wstr.write(c_int(1 << (task[2] + 1)))
            #     wstr.write(c_uint8(0))

            #     msg = ServerGameMessage(packet.objid, GameMessageID.NOTIFY_MISSION_TASK, wstr)
            #     self.server.rnserver.send(msg, address)

            wstr = WriteStream()
            wstr.write(c_int(mission_id))
            wstr.write(c_int(2))
            wstr.write(c_bit(False))

            msg = ServerGameMessage(responder_objid, GameMessageID.NOTIFY_MISSION, wstr)

        self.server.rnserver.send(msg, address)

    def collected(self, packet, address, stream):
        """
        Handles the has been collected game message
        """

        objid = stream.read(c_int64)

        print(f'Collected object')
        print(f'ID: {packet.objid}')
        print(f'Player: {objid}')

        session = self.server.handle_until_return('session:get_session', address)
        char = self.server.handle_until_return('char:characters', session.account.user.id)[session.account.front_character]
        clone = self.server.handle_until_return('world:get_clone', session.clone)
        char_missions = self.server.handle_until_return('char:get_missions', char.id)

        objs = [x for x in clone.objects if x.objid == packet.objid]

        if objs:
            obj = objs[0]

            for char_mission in [x for x in char_missions if x.state == 2]:
                tasks = self.server.handle_until_return('world:get_mission_tasks', char_mission.mission)

                for task in tasks:
                    if task[3] == obj.lot and task[2] == 3:
                        char_mission.progress += 1
                        char_mission.save()

                        wstr = WriteStream()

                        wstr.write(c_int(char_mission.mission))
                        wstr.write(c_int(1 << (tasks.index(task) + 1)))
                        wstr.write(c_uint8(1))
                        wstr.write(c_float(char_mission.progress + (clone.zone << 8)))

                        msg = ServerGameMessage(objid, GameMessageID.NOTIFY_MISSION_TASK, wstr)

                        self.server.rnserver.send(msg, address)

                        return
