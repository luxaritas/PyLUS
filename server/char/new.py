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
        session = self.server.handle_until_return('session:get_session', address)
        # TODO: Do validation which could result in other status codes
        status = 'success'

        # NOTE: shouldn't we check if len(characters) >= 4?

        first = open('./client_assets/names/minifigname_first.txt', 'r').readlines()
        middle = open('./client_assets/names/minifigname_middle.txt', 'r').readlines()
        last = open('./client_assets/names/minifigname_last.txt', 'r').readlines()

        part1 = first[packet.predef_name1].strip()
        part2 = middle[packet.predef_name2].strip()
        part3 = last[packet.predef_name3].strip()

        new_char = self.server.handle_until_return('char:create_character', session.account,
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

        self.server.rnserver.send(MinifigureCreateResponse(status), address)
        self.server.handle_until_value('char:send_char_list', True, session)

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

    @property
    def status_code(self):
        """
        Returns a dict of auth status codes
        """
        return {
            'success': 0x00,
            'name_not_allowed': 0x02,
            'predef_in_use': 0x03,
            'custom_in_use': 0x04,
        }.get(self.status)
    
    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)

        stream.write(c_uint8(self.status_code))
