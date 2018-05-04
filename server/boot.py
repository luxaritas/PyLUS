#!/usr/bin/python3.6

"""
Main file
"""

import asyncio
import inspect
import logging
import yaml
import os
import sys

sys.path.append(os.path.abspath('..'))

from pyraknet.server import Server as RNServer, Event as RNEvent
from django.conf import settings
from django.apps import apps

from plugin import get_plugins
from cms.cms import settings as cms_settings

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# --- Make the CMS available within Pylus ---
settings.configure(
    DATABASES=cms_settings.DATABASES,
    TIME_ZONE=cms_settings.TIME_ZONE,
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'cms.game',
    ],
)
apps.populate(settings.INSTALLED_APPS)


class Server:
    """
    Main server class
    """
    def __init__(self, server_type: str, host: str, port: int, max_connections: int, config: dict):
        self.rnserver = RNServer((host, port), max_connections, b'3.25 ND1')
        self.rnserver.add_handler(RNEvent.NetworkInit, lambda addr: self.handle('rn:network_init', addr))
        self.rnserver.add_handler(RNEvent.Disconnect, lambda addr: self.handle('rn:disconnect', addr))
        self.rnserver.add_handler(RNEvent.UserPacket, lambda data, addr: self.handle('rn:user_packet', data, addr))
        self.config = config
        self.type = server_type
        self.plugins = []
        self.handlers = {}
        self.packets = {}
        self.connections = {}

        self.register_plugins('core')
        self.register_plugins('core.django_cms')
        self.register_plugins(self.type if self.type in ['auth', 'char', 'chat'] else 'world')

    def register_plugins(self, package: str):
        """
        Registers plugins
        """
        new_plugins = [UserPlugin(self) for UserPlugin in get_plugins(package)]
        self.plugins += new_plugins

        for plugin in new_plugins:
            for (event, handler, priority) in plugin.actions():
                self.handlers.setdefault(event, []).append((handler, priority))

            for packet in plugin.packets():
                existing = self.packets.get(packet.packet_name)

                if existing:
                    mod = inspect.getmodule(existing)
                    raise KeyError(
                        f'Multiple packets cannot be registered for the same packet name. {mod} is already registered')

                self.packets[packet.packet_name] = packet

        for plugin in new_plugins:
            name = self.type.upper()
            mod = plugin.__module__
            actions = [action.event for action in plugin.actions()]

            log.info(f'{name} - Registered plugin: {mod} consuming {actions}')

    def get_ordered_handlers(self, event):
        """
        Gets ordered handlers
        """
        return sorted(self.handlers.get(event, []), key=lambda handler: handler[1])

    def handle(self, event, *args, **kwargs):
        """
        Registers a handler
        """
        handlers = self.get_ordered_handlers(event)
        results = []
        for handler, _ in handlers:
            results.append(handler(*args, **kwargs))

        return results

    def handle_until_value(self, event, value, *args, value_method='equals', **kwargs):
        """
        Handles something until a value matches
        """
        handlers = self.get_ordered_handlers(event)
        for handler, _ in handlers:
            result = handler(*args, **kwargs)
            if ((value_method == 'equals' and result == value) or
                    (value_method == 'not equals' and result != value) or
                    (value_method == 'in' and result in value) or
                    (value_method == 'not in' and not result in value)):
                return True

        return False

    def handle_until_return(self, event, *args, **kwargs):
        """
        Handles something until a value returns
        """
        handlers = self.get_ordered_handlers(event)
        for handler, _ in handlers:
            result = handler(*args, **kwargs)
            if result is not None:
                return result

        return None

    def add_connection(self, address, uid):
        self.connections[address] = {'uid': uid}


if __name__ == '__main__':
    try:
        with open('config.yml') as f:
            s_config = yaml.load(f)
    except FileNotFoundError:
        with open('config.default.yml') as f:
            s_config = yaml.load(f)
    servers = {}
    for s_type, conf in s_config['servers'].items():
        if conf['enabled']:
            servers[s_type] = Server(s_type, conf['listen_host'], conf['listen_port'], conf['max_connections'],
                                     s_config)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
