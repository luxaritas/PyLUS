"""
Core server implementation and startup
"""

import asyncio
import inspect
import logging
import os
import sys
import yaml

from event_dispatcher import EventDispatcher

from pyraknet.server import Server as RNServer
from pyraknet.messages import Message as RNMessage
from pyraknet.transports.abc import Connection
from pyraknet.replicamanager import ReplicaManager

from .plugin import get_derivatives, Plugin
from cms.cms import settings as cms_settings
from conf_manage import MainConfig

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Server:
    """
    Main server class
    """
    def __init__(self, server_type: str, host: str, port: int, max_connections: int, config: MainConfig):
        self.rndispatcher = EventDispatcher()
        self.rnserver = RNServer((host, port), max_connections, b'3.25 ND1', None, self.rndispatcher)
        self.rndispatcher.add_listener(RNMessage.UserPacket, self.on_user_packet)
        self.config = config
        self.type = server_type
        self.plugins = []
        self.handlers = {}
        self.packets = {}
        
        if self.type not in ['auth', 'chat', 'char']:
            self.repman = ReplicaManager(self.rndispatcher)

        self.register_plugins('server.core')
        if self.type in ['auth', 'chat']:
            self.register_plugins('server.' + self.type)
        else:
            self.register_plugins('server.world')
            if self.type != 'char':
                self.register_plugins('server.world.zone')
        
        log.info(f'{self.type.upper()} - Started up')

    def on_user_packet(self, data, conn):
        self.handle('rn:user_packet', data, conn)

    def register_plugins(self, package: str):
        """
        Registers plugins
        """
        new_plugins = [UserPlugin(self) for UserPlugin in get_derivatives(package, Plugin)]
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

            log.debug(f'{name} - Registered plugin: {mod} consuming {actions}')

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


def start(config: MainConfig):
    servers = {}
    # for srv_type, conf in config['servers'].items():
    for server in config.servers:
        if server.enabled:
            servers[server.name] = Server(server.name, server.listen_host, server.listen_port, server.max_connections, config)
    #     if conf['enabled']:
    #         servers[srv_type] = Server(srv_type, conf['listen_host'], conf['listen_port'], conf['max_connections'], config)
    return servers
