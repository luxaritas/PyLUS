import os, sys, inspect
pylus_path = os.path.abspath("..")
sys.path.append(pylus_path)

import asyncio, logging
import yaml
from pyraknet.server import Server as RNServer, Event as RNEvent
from plugin import Plugin, get_plugins
from cms.cms import settings as cms_settings
from django.conf import settings
from django.apps import apps

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# --- Make the CMS available within Pylus ---
settings.configure(
    DATABASES = cms_settings.DATABASES,
    TIME_ZONE = cms_settings.TIME_ZONE,
    INSTALLED_APPS = [
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'cms.game',
    ],
)
apps.populate(settings.INSTALLED_APPS)


class Server:
    def __init__(self, server_type, host, port, max_connections, config):
        self.rnserver = RNServer((host, port), max_connections, b'3.25 ND1')
        self.rnserver.add_handler(RNEvent.NetworkInit, lambda addr: self.handle('rn:network_init', addr))
        self.rnserver.add_handler(RNEvent.Disconnect, lambda addr: self.handle('rn:disconnect', addr))
        self.rnserver.add_handler(RNEvent.UserPacket, lambda data, addr: self.handle('rn:user_packet', data, addr))
        self.config = config
        self.type = server_type
        self.plugins = []
        self.handlers = {}
        self.packets = {}
        
        self.register_plugins('core')
        self.register_plugins(self.type if self.type in ['auth', 'char', 'chat'] else 'world')

    def register_plugins(self, package):
        new_plugins = [UserPlugin(self) for UserPlugin in get_plugins(package)]
        self.plugins += new_plugins

        for plugin in new_plugins:
            for (event, handler, priority) in plugin.actions():
                self.handlers.setdefault(event, []).append((handler, priority))
            for packet in plugin.packets():
                existing = self.packets.get(packet.packet_name)
                if existing is not None:
                    raise ArgumentError('Multiple packets cannot be registered for the same packet name. {} is already registered'.format(inspect.getmodule(existing)))
                self.packets[packet.packet_name] = packet

        for plugin in new_plugins:       
            log.info('{} - Registered plugin: {} consuming {}'.format(
                      self.type.upper(),
                      plugin.__module__,
                      [action.event for action in plugin.actions()])
                    )
        
    def get_ordered_handlers(self, event):
        return sorted(self.handlers.get(event, []), key=lambda handler: handler[1])

    def handle(self, event, *args, **kwargs):
        handlers = self.get_ordered_handlers(event)
        results = []
        for handler, priority in handlers:
            results.append(handler(*args, **kwargs))

        return results

    def handle_until_value(self, event, value, *args, value_method='equals', **kwargs):
        handlers = self.get_ordered_handlers(event)
        for handler, priority in handlers:
            result = handler(*args, **kwargs)
            if ((value_method == 'equals' and result == value) or
               (value_method == 'not equals' and result != value) or
               (value_method == 'in' and result in value) or
               (value_method == 'not in' and not result in value)):
                return True

        return False
          
    def handle_until_return(self, event, *args, **kwargs):
        handlers = self.get_ordered_handlers(event)
        for handler, priority in handlers:
            result = handler(*args, **kwargs)
            if result is not None:
                return result
      
        return None
      
if __name__ == '__main__':
    try:
        with open('config.yml') as f:
            config = yaml.load(f)
    except FileNotFoundError:
        with open('config.default.yml') as f:
            config = yaml.load(f)
    servers = {}
    for server_type, conf in config['servers'].items():
        if conf['enabled']:
            servers[server_type] = Server(server_type, conf['listen_host'], conf['listen_port'], conf['max_connections'], config)
    
    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
    