"""
Create character
"""

from pyraknet.bitstream import Serializable, c_uint32, c_uint8

from server.char.list import CharacterListResponse, Character as Minifigure
from server.plugin import Plugin, Action
from server.structs import Packet


class CreateCharacter(Plugin):
    """
    Create character plugin
    """
    def actions(self):
        """
        Returns list of actions
        """
        return [
            Action('pkt:minifig_create_request', self.minifig_create_request, 10)
        ]

    def packets(self):
        """
        Returns list of packets
        """
        return [
            MinifigureCreateRequest
        ]

    def minifig_create_request(self, packet, address):
        """
        Handles the request
        """
        uid = self.server.handle_until_return('session:get_session', address).account.user.id
        status = 0x00

        characters = self.server.handle_until_return('char:characters', uid)

        # NOTE: shouldn't we check if len(characters) >= 4?

        first = open('./names/minifigname_first.txt', 'r').readlines()
        middle = open('./names/minifigname_middle.txt', 'r').readlines()
        last = open('./names/minifigname_last.txt', 'r').readlines()

        part1 = first[packet.predef_name1].strip()
        part2 = middle[packet.predef_name2].strip()
        part3 = last[packet.predef_name3].strip()

        self.server.handle('char:create_character', uid,
                           len(characters) + 1,  # slot
                           part1 + part2 + part3,  # character name
                           packet.name,  # unapproved name
                           False,  # is name rejected
                           packet.shirt_color,  # shirt color
                           packet.shirt_style,  # shirt style
                           packet.pants_color,  # pants color
                           packet.hair_style,  # hair style
                           packet.hair_color,  # hair color
                           packet.lh,  # lh
                           packet.rh,  # rh
                           packet.eyebrows,  # eyebrows
                           packet.eyes,  # eyes
                           packet.mouth,  # mouth
                           1000,  # last zone
                           0,  # last instance
                           0,  # last clone
                           0)  # last login

        ftp = self.server.handle_until_value('auth:get_free_to_play', True, uid)

        serializable_chars = []

        characters = self.server.handle_until_return('char:characters', uid)

        for character in characters:
            serializable_char = Minifigure(character_id=character.id,
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

            serializable_chars.append(serializable_char)

        res = MinifigureCreateResponse(status)
        res2 = CharacterListResponse(serializable_chars, len(serializable_chars) - 1)

        self.server.rnserver.send(res, address)
        self.server.rnserver.send(res2, address)


class MinifigureCreateRequest(Packet):
    """
    Minifigure create request packet
    """
    packet_name = 'minifig_create_request'

    def __init__(self, name, predef_name1, predef_name2, predef_name3, unknown1, shirt_color, shirt_style, pants_color,
                 hair_style, hair_color, lh, rh, eyebrows, eyes, mouth):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    @classmethod
    def deserialize(cls, stream):
        """
        Deserializes the packet
        """
        name = stream.read(str, allocated_length=33)
        predef1 = stream.read(c_uint32)
        predef2 = stream.read(c_uint32)
        predef3 = stream.read(c_uint32)

        unknown = stream.read(bytes, allocated_length=9)

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

        return cls(name, predef1, predef2, predef3, unknown, shirt_color, shirt_style, pants_color, hair_style, hair_color,
                   lh, rh, eyebrows, eyes, mouth)


class MinifigureCreateResponse(Packet):
    """
    Minifigure create response packet
    """
    packet_name = 'minifig_create_response'

    def __init__(self, status):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)

        stream.write(c_uint8(self.status))
