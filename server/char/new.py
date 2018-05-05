"""
Create character
"""

from pyraknet.bitstream import Serializable, c_uint32, c_uint8

from char.list import CharacterListResponse, Character as Minifigure
from plugin import Plugin, Action, Packet
from structs import CString


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
        uid = 1
        status = 0x00

        characters = self.server.handle_until_return('char:characters', uid)

        # NOTE: shouldn't we check if len(characters) >= 4?

        self.server.handle('char:create_character', uid,
                           len(characters) + 1,  # slot
                           packet.name,  # character name
                           '',  # unapproved name
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
                           0,  # last zone
                           0,  # last instance
                           0,  # last clone
                           0)  # last login

        ftp = self.server.handle_until_value('auth:get_free_to_play', True, uid)

        char = Minifigure(character_id=len(characters) + 1,
                          unknown1=0,
                          character_name=packet.name,
                          character_unapproved_name='',
                          is_name_rejected=False,
                          free_to_play=ftp,
                          unknown2=0,
                          shirt_color=packet.shirt_color,
                          shirt_style=packet.shirt_style,
                          pants_color=packet.pants_color,
                          hair_style=packet.hair_style,
                          hair_color=packet.hair_color,
                          lh=packet.lh,
                          rh=packet.rh,
                          eyebrows=packet.eyebrows,
                          eyes=packet.eyes,
                          mouth=packet.mouth,
                          unknown3=0,
                          last_zone=0,
                          last_instance=0,
                          last_clone=0,
                          last_login=0,
                          items=[])

        chars = list(characters)
        chars.append(char)

        res = MinifigureCreateResponse(status)
        res2 = CharacterListResponse(chars, len(chars))

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

        unknown = stream.read(c_uint8, allocated_length=9)

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
