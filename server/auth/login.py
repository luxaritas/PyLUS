"""
Login plugin
"""

from pyraknet.bitstream import Serializable, c_uint8, c_uint16, c_uint32, c_uint64, c_bool
from plugin import Plugin, Action, Packet
from structs import LUHeader, CString, GameVersion


class Login(Plugin):
    """
    Login plugin class
    """
    def actions(self):
        """
        Returns actions for this plugin
        """
        return [
            Action('pkt:login_request', self.login_request, 10)
        ]

    def packets(self):
        """
        Returns packets for this plugin
        """
        return [
            LoginRequest,
            LoginResponse
        ]

    def login_request(self, packet, address):
        """
        Handles a login request
        """
        if not self.server.handle_until_value('auth:check_credentials', True, packet.username, packet.password):
            auth_status = 'bad_credentials'
            uid = None
        else:
            uid = self.server.connections('auth:get_user_id', True, address)

            if self.server.handle_until_value('auth:check_banned', True, uid, address):
                auth_status = 'banned'
            elif self.server.handle_until_value('auth:check_permission', False, 'login', uid):
                auth_status = 'not_permitted'
            elif self.server.handle_until_value('auth:check_locked', True, uid):
                # User has failed entering their password too many times
                auth_status = 'locked'
            elif self.server.handle_until_value('auth:check_activated', False, uid):
                # User needs to take some step to activate their account (ex, confirm email)
                auth_status = 'not_activated'
            elif self.server.handle_until_value('auth:check_schedule', False, uid):
                # Schedule set up by parent for time allowed to play does not allow play at this time
                auth_status = 'schedule_blocked'
            else:
                auth_status = 'success'

            if auth_status == 'success':
                token = self.server.handle_until_return('auth:token', uid)
            else:
                token = ''

        permission_error = 'You do not have permission to log in to this server' if auth_status == 'not_permitted' else ''

        if uid:
            self.server.handle_until_value('auth:set_address', uid, address)
            new_subscriber = self.server.handle_until_value('auth:new_subscriber', True, uid)
            ftp = self.server.handle_until_value('auth:free_to_play', True, uid)
        else:
            new_subscriber = False
            ftp = False

        char_ip = self.server.config['servers']['char']['public_host']
        chat_ip = self.server.config['servers']['chat']['public_host']
        char_port = self.server.config['servers']['char']['public_port']
        chat_port = self.server.config['servers']['chat']['public_port']

        res = LoginResponse(auth_status, token, char_ip, chat_ip, char_port, chat_port, new_subscriber, ftp, permission_error)

        self.server.rnserver.send(res, address)


class LoginRequest(Packet):
    """
    Login request packet class
    """
    packet_name = 'login_request'
    allow_without_session = True

    @classmethod
    def deserialize(cls, stream):
        """
        Deserializes the packet
        """
        return cls(username=stream.read(str, allocated_length=33),
                   password=stream.read(str, allocated_length=41),
                   language_id=stream.read(c_uint16),
                   unknown=stream.read(c_uint8),
                   process_memory_info=stream.read(str, allocated_length=256),
                   graphics_driver_info=stream.read(str, allocated_length=128),
                   processor_count=stream.read(c_uint32),
                   processor_type=stream.read(c_uint32),
                   processor_level=stream.read(c_uint16),
                   processor_revision=stream.read(c_uint16),
                   unknown1=stream.read(c_uint32),
                   os_major_version=stream.read(c_uint32),
                   os_minor_version=stream.read(c_uint32),
                   os_build_number=stream.read(c_uint32),
                   os_platform_id=stream.read(c_uint32))

class LoginResponse(Packet):
    """
    Login response packet
    """

    packet_name = 'login_response'
    allow_without_session = True

    def __init__(self, auth_status, auth_token, char_ip, chat_ip, char_port, chat_port, new_subscriber, is_ftp, permission_error,
                 client_version=GameVersion(1, 10, 64), localization='US',
                 unknown='Talk_Like_A_Pirate', unknown1='', unknown2='0', unknown3='00000000-0000-0000-0000-000000000000',
                 unknown4=0, unknown5=0):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    @property
    def auth_status_code(self):
        """
        Returns a dict of auth status codes
        """
        return {
            'success': 0x01,
            'banned':  0x02,
            'not_permitted': 0x05,
            'bad_credentials': 0x06,
            'locked': 0x07,
            'schedule_blocked': 0x0d,
            'not_activated': 0x0e,
        }.get(self.auth_status)

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)
        stream.write(c_uint8(self.auth_status_code))
        stream.write(CString(self.unknown, allocated_length=33))
        stream.write(CString(self.unknown1, allocated_length=33*7))
        stream.write(self.client_version)
        stream.write(self.auth_token, allocated_length=33)
        stream.write(CString(self.char_ip, allocated_length=33))
        stream.write(CString(self.chat_ip, allocated_length=33))
        stream.write(c_uint16(self.char_port))
        stream.write(c_uint16(self.chat_port))
        stream.write(CString(self.unknown2, allocated_length=33))
        stream.write(CString(self.unknown3, allocated_length=37))
        stream.write(c_uint32(self.unknown4))
        stream.write(CString(self.localization, allocated_length=3))
        stream.write(c_bool(self.new_subscriber))
        stream.write(c_bool(self.is_ftp))
        stream.write(c_uint64(self.unknown5))
        stream.write(self.permission_error, length_type=c_uint16)
        # TODO: Implement stamps
        stream.write(c_uint32(4))
