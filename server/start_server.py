"""
Core server implementation and startup
"""

import asyncio
import inspect
import logging
import os
import sys
import yaml

from pyraknet.server import Server as RNServer, Event as RNEvent
from pyraknet.replicamanager import ReplicaManager

from .plugin import get_plugins
from cms.cms import settings as cms_settings

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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

        self.register_plugins('server.core')
        if self.type in ['auth', 'chat']:
            self.register_plugins('server.' + self.type)
        else:
            self.register_plugins('server.world')
            if self.type != 'char':
                self.register_plugins('server.world.zone')

        if self.type not in ['auth', 'chat', 'char']:
            self.rnserver.file_logged_packets.update(['ReplicaManagerConstruction'])
            self.repman = ReplicaManager(self.rnserver)

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

def start(config):
    servers = {}
    for srv_type, conf in config['servers'].items():
        if conf['enabled']:
            servers[srv_type] = Server(srv_type, conf['listen_host'], conf['listen_port'], conf['max_connections'], config)
    return servers
