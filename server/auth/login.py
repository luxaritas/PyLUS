from pyraknet.bitstream import WriteStream, c_uint8, c_uint16, c_uint32, c_uint64, c_bool
from plugin import Plugin
from structs import LUHeader

class Handshake(Plugin):
    def actions(self):
        return {
            'pkt:login_request': (self.login, 10)
        }
    
    def login(self, data, address):
        username = data.read(str, allocated_length=33)
        password = data.read(str, allocated_length=41)
        language_id = data.read(c_uint16)
        unknown0 = data.read(c_uint8)
        process_memory_info = data.read(str, allocated_length=256)
        graphics_driver_info = data.read(str, allocated_length=128)
        processor_count = data.read(c_uint32)
        processor_type = data.read(c_uint32)
        processor_level = data.read(c_uint16)
        processor_revision = data.read(c_uint16)
        unknown1 = data.read(c_uint32)
        os_major_version = data.read(c_uint32)
        os_minor_version = data.read(c_uint32)
        os_build_number = data.read(c_uint32)
        os_platform_id = data.read(c_uint32)
        
        if not self.server.handle_until_value('auth:check_credentials', True, username, password):
            auth_status = 'bad_credentials'
        elif self.server.handle_until_value('auth:check_banned', True, username, address):
            auth_status = 'banned'
        elif self.server.handle_until_value('auth:check_permission', False, 'login', username):
            auth_status = 'not_permitted'
        elif self.server.handle_until_value('auth:check_locked', True, username):
            # User has failed entering their password too many times
            auth_status = 'locked'
        elif self.server.handle_until_value('auth:check_activated', False, username):
            # User needs to take some step to activate their account (ex, confirm email)
            auth_status = 'not_activated'
        elif self.server.handle_until_value('auth:check_schedule', False, username):
            # Schedule set up by parent for time allowed to play does not allow play at this time
            auth_status = 'schedule_blocked'
        else:
            auth_status = 'success'
        
        res = WriteStream()
        # Packet
        res.write(LUHeader('login_response'))
        # Return code
        res.write(c_uint8({
            'success': 0x01,
            'banned':  0x02,
            'not_permitted': 0x05,
            'bad_credentials': 0x06,
            'locked': 0x07,
            'schedule_blocked': 0x0d,
            'not_activated': 0x0e,
        }.get(auth_status)))
        # ???
        res.write(b'Talk_Like_A_Pirate', allocated_length=33)
        res.write(b'', allocated_length=33*7)
        # Client Version (major, current, minor)
        res.write(c_uint16(1))
        res.write(c_uint16(10))
        res.write(c_uint16(64))
        # Auth token
        if auth_status is 'success':
            token = self.server.handle_until_return('auth:token', username)
        else:
            token = ''
        res.write(token, allocated_length=33)
        # Char and Chat servers
        res.write(bytes(self.server.config['servers']['char']['public_host'], 'utf8'), allocated_length=33)
        res.write(bytes(self.server.config['servers']['chat']['public_host'], 'utf8'), allocated_length=33)
        res.write(c_uint16(self.server.config['servers']['char']['public_port']))
        res.write(c_uint16(self.server.config['servers']['chat']['public_port']))
        # ???
        res.write(b'0', allocated_length=33)
        res.write(b'00000000-0000-0000-0000-000000000000', allocated_length=37)
        res.write(c_uint32(0))
        # Localization
        res.write(b'US', allocated_length=3)
        # First time subscriber screen
        res.write(c_bool(False))
        # Is FTP
        res.write(c_bool(False))
        # ???
        res.write(c_uint64(0))
        # Custom error for login code 0x05
        permission_error = 'You do not have permission to log in to this server' if auth_status is 'not_permitted' else ''
        res.write(permission_error, length_type=c_uint16)
        # Stamps - Not implemented ATM
        res.write(c_uint32(4))
        
        self.server.rnserver.send(res, address)
        