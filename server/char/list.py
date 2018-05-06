"""
Character listt
"""

from pyraknet.bitstream import Serializable, c_int64, c_uint8, c_uint16, c_uint32, c_uint64, c_bool

from plugin import Plugin, Action, Packet


class CharacterList(Plugin):
    """
    Character list plugin
    """
    def actions(self):
        """
        Returns all actions
        """
        return [
            Action('pkt:character_list_request', self.character_list_request, 10)
        ]

    def packets(self):
        """
        Returns all packets
        """
        return [
            ClientCharacterListRequest,
            CharacterListResponse
        ]

    def character_list_request(self, packet, address):
        """
        Handles a char list request
        """
        uid = self.server.handle_until_return('auth:get_user_id', address)

        front_char = self.server.handle_until_return('char:front_char_index', uid)
        characters = self.server.handle_until_return('char:characters', uid)

        serializable_characters = []

        for character in characters:
            serializable_character = Character(character_id=character.id,
                                               unknown1=0,
                                               character_name=character.name,
                                               character_unapproved_name=character.unapproved_name,
                                               is_name_rejected=character.is_name_rejected,
                                               free_to_play=character.account.free_to_play,
                                               unknown2=0,
                                               shirt_color=character.shirt_color,
                                               shirt_style=character.shirt_style,
                                               pants_color=character.pants_color,
                                               hair_style=character.hair_style,
                                               hair_color=character.hair_color,
                                               lh=character.lh,
                                               rh=character.rh,
                                               eyebrows=character.eyebrows,
                                               eyes=character.eyes,
                                               mouth=character.mouth,
                                               unknown3=0,
                                               last_zone=character.last_zone,
                                               last_instance=character.last_instance,
                                               last_clone=character.last_clone,
                                               last_login=character.last_login,
                                               items=[])

            serializable_characters.append(serializable_character)

        res = CharacterListResponse(serializable_characters, 0 if front_char > len(characters) -1 else front_char)

        self.server.rnserver.send(res, address)


class ClientCharacterListRequest(Packet):
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

    def __init__(self, characters, front_char):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)

        stream.write(c_uint8(len(self.characters)))
        stream.write(c_uint8(self.front_char))

        for character in self.characters:
            stream.write(character)


class Character(Serializable):
    """
    Character serializable
    """
    def __init__(self, character_id, unknown1, character_name, character_unapproved_name, is_name_rejected, free_to_play,
                 unknown2, shirt_color, shirt_style, pants_color, hair_style, hair_color, lh, rh, eyebrows, eyes, mouth,
                 unknown3, last_zone, last_instance, last_clone, last_login, items):
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
        self.items = items


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
        stream.write(b'\x00' * 10)
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
        stream.write(c_uint16(len(self.items)))
        for item in self.items:
            stream.write(c_uint32(item))

    @classmethod
    def deserialize(cls, stream):
        """
        Deserializes the packet
        """
        character_id = stream.read(c_int64)
        unknown1 = stream.read(c_uint32)
        character_name = stream.read(str, allocated_length=33)
        character_unapproved_name = stream.read(str, allocated_legnth=33)
        is_name_rejected = stream.read(c_bool)
        free_to_play = stream.read(c_bool)
        unknown2 = stream.read(bytes, allocated_length=10)
        shirt_color = stream.read(c_uint32)
        shirt_style = stream.read(c_uint32)
        pants_color = stream.read(c_uint32)
        hair_style = stream.read(c_uint32)
        hair_color = stream.read(c_uint32)
        lh = stream.read(c_uint32)
        rh = stream.read(c_uint32)
        eyebrows = stream.read(c_uint32)
        eyes = stream.read(c_uint32)
        mouth = stream.read(c_uint32)
        unknown3 = stream.read(c_uint32)
        last_zone = stream.read(c_uint16)
        last_instance = stream.read(c_uint16)
        last_clone = stream.read(c_uint32)
        last_login = stream.read(c_uint64)
        item_count = stream.read(c_uint16)
        items = []

        for _ in range(item_count):
            items.append(stream.read(c_uint32))

        return cls(character_id, unknown1, character_name, character_unapproved_name, is_name_rejected, free_to_play,
                   unknown2, shirt_color, shirt_style, pants_color, hair_style, hair_color, lh, rh, eyebrows, eyes, mouth,
                   unknown3, last_zone, last_instance, last_clone, last_login, items)
