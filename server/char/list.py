"""
Character listt
"""

from pyraknet.bitstream import Serializable, c_int64, c_uint8, c_uint16, c_uint32, c_uint64, c_bool

from server.plugin import Plugin, Action
from server.structs import Packet


class CharacterList(Plugin):
    """
    Character list plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('pkt:character_list_request', self.character_list_request, 10),
            Action('char:send_list', self.send_char_list, 10),
        ]

    def packets(self):
        """
        Returns all packets
        """
        return [
            CharacterListRequest,
            CharacterListResponse
        ]

    def character_list_request(self, packet, address):
        """
        Handles a char list request
        """
        session = self.server.handle_until_return('session:get_session', address)
        self.server.handle_until_value('char:send_char_list', True, session)
        
        
    def send_char_list(self, session):
        characters = self.server.handle_until_return('char:characters', session.account)
        front_char = self.server.handle_until_return('char:front_char', characters)

        serializable_characters = []

        for character in characters:
            serializable_character = Character(character.objid,
                                               character.name,
                                               character.unapproved_name,
                                               character.is_name_rejected,
                                               character.account.free_to_play,
                                               character.shirt_color,
                                               character.shirt_style,
                                               character.pants_color,
                                               character.hair_style,
                                               character.hair_color,
                                               character.lh,
                                               character.rh,
                                               character.eyebrows,
                                               character.eyes,
                                               character.mouth,
                                               character.last_zone,
                                               character.last_instance,
                                               character.last_clone,
                                               character.last_login,
                                               [])

            serializable_characters.append(serializable_character)

        res = CharacterListResponse(serializable_characters, serializable_characters.index(front_char))
        self.server.rnserver.send(res, (session.ip, session.port))
        
        return True


class CharacterListRequest(Packet):
    """
    Client character list request packet
    """
    packet_name = 'character_list_request'

    @classmethod
    def deserialize(cls, stream):
        """
        Deserializes the packet
        """
        return cls()


class CharacterListResponse(Packet):
    """
    Character list response packet
    """
    packet_name = 'character_list_response'

    def __init__(self, characters, front_char_id):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)

        stream.write(c_uint8(len(self.characters)))
        stream.write(c_uint8(self.front_char_id))

        for character in self.characters:
            stream.write(character)


class Character(Serializable):
    """
    Character serializable
    """
    def __init__(self, character_id, character_name, character_unapproved_name, is_name_rejected, free_to_play,
                 shirt_color, shirt_style, pants_color, hair_style, hair_color, lh, rh, eyebrows, eyes, mouth,
                 last_zone, last_instance, last_clone, last_login, equipped_items, unknown1=0, unknown2=b'\x00'*10, unknown3=0):
        self.character_id = character_id
        self.unknown1 = unknown1
        self.character_name = character_name
        self.character_unapproved_name = character_unapproved_name
        self.is_name_rejected = is_name_rejected
        self.free_to_play = free_to_play
        self.unknown2 = unknown2
        self.shirt_color = shirt_color
        self.shirt_style = shirt_style
        self.pants_color = pants_color
        self.hair_style = hair_style
        self.hair_color = hair_color
        self.lh = lh
        self.rh = rh
        self.eyebrows = eyebrows
        self.eyes = eyes
        self.mouth = mouth
        self.unknown3 = unknown3
        self.last_zone = last_zone
        self.last_instance = last_instance
        self.last_clone = last_clone
        self.last_login = last_login
        self.equipped_items = equipped_items


    def serialize(self, stream):
        """
        Serializes the packet
        """
        stream.write(c_int64(self.character_id))
        stream.write(c_uint32(self.unknown1))
        stream.write(self.character_name, allocated_length=33)
        stream.write(self.character_unapproved_name, allocated_length=33)
        stream.write(c_bool(self.is_name_rejected))
        stream.write(c_bool(self.free_to_play))
        stream.write(self.unknown2)
        stream.write(c_uint32(self.shirt_color))
        stream.write(c_uint32(self.shirt_style))
        stream.write(c_uint32(self.pants_color))
        stream.write(c_uint32(self.hair_style))
        stream.write(c_uint32(self.hair_color))
        stream.write(c_uint32(self.lh))
        stream.write(c_uint32(self.rh))
        stream.write(c_uint32(self.eyebrows))
        stream.write(c_uint32(self.eyes))
        stream.write(c_uint32(self.mouth))
        stream.write(c_uint32(self.unknown3))
        stream.write(c_uint16(self.last_zone))
        stream.write(c_uint16(self.last_instance))
        stream.write(c_uint32(self.last_clone))
        stream.write(c_uint64(self.last_login))
        stream.write(c_uint16(len(self.equipped_items)))
        for item in self.items:
            stream.write(c_uint32(item))
