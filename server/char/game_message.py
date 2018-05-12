"""
Game message handling
"""

from pyraknet.bitstream import c_int64, c_int

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
        print(f'Unhandled game message with ID: {packet.message_id}')
