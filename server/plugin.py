"""
Plugin stuff
"""

import inspect
import importlib
import pkgutil

from abc import ABC, abstractmethod
from typing import List, NamedTuple, Callable, overload, TYPE_CHECKING
from bitstream import Serializable, WriteStream, ReadStream
if (TYPE_CHECKING):
    from .start_server import Server
from .structs import LUHeader

class Packet(Serializable):
    """
    Packet class
    """
    allow_without_session = False

    @overload
    def __init__(self):
        pass

    def __init__(self, header: LUHeader = None, data: bytes = None, **kwargs):
        packet_name = getattr(self.__class__, 'packet_name', None)

        if packet_name:
            self.header = LUHeader(packet_name)
            for prop, val in kwargs.items():
                setattr(self, prop, val)
        elif header and data != None:
            self.header = header
            self.data = data
        else:
            raise KeyError('Packets must either be instantiated from a base class with a packet_name, Packet.deserialize(), or with a header and data argument')

    def __bytes__(self):
        stream = WriteStream()
        self.serialize(stream)
        return bytes(stream)

    def serialize(self, stream: WriteStream):
        """
        Serialize the packet
        """
        self.header.serialize(stream)
        if getattr(self, 'data', None) is not None:
            stream.write(self.data)

    @classmethod
    def deserialize(cls, stream: ReadStream, packet_types):
        """
        Deserialize the packet
        """
        header = LUHeader.deserialize(stream)
        packet = packet_types.get(getattr(header, 'packet_name', None))

        if packet:
            return packet.deserialize(stream)

        return cls(header=header, data=stream.read_remaining())


class Action(NamedTuple):
    """
    Action tuple
    """
    event: str
    handler: Callable
    priority: int


class Plugin(ABC):
    """
    Plugin class
    """
    def __init__(self, server: 'Server'):
        self.server = server

    @abstractmethod
    def actions(self) -> List[Action]:
        """
        Returns a list of actions
        """
        return []

    def packets(self) -> List[Packet]:
        """
        Returns a list of packets
        """
        return []

def isderivative(member, cls: object) -> bool:
    """
    Checks if member is a plugin
    """
    return inspect.isclass(member) and issubclass(member, cls) and member is not cls

def get_derivatives(package, base_class):
    """
    Get plugins from a package

    Via https://stackoverflow.com/a/25562415/
    """
    result = []
    if isinstance(package, str):
        package = importlib.import_module(package)
    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        module = importlib.import_module(full_name)

        if is_pkg:
            result += get_derivatives(full_name, base_class)
        else:
            for _, plugin in inspect.getmembers(module, lambda module: isderivative(module, base_class)):
                result.append(plugin)

    return result
