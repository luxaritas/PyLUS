import inspect, importlib, pkgutil
from abc import ABC, abstractmethod
from typing import List, NamedTuple, Callable, overload
from pyraknet.bitstream import Serializable, WriteStream
from structs import LUHeader
    
class Packet(Serializable):
    @overload
    def __init__(self):
        pass
    
    @overload
    def __init__(self, header:LUHeader, data:bytes):
        pass
    
    def __init__(self, header=None, data=None, **kwargs):
        packet_name = getattr(self.__class__, 'packet_name', None)
        if packet_name is not None:
            self.header = LUHeader(packet_name)
            for prop, val in kwargs.items():
                setattr(self, prop, val)
        
        elif header is not None and data is not None:
            self.header = header
            self.data = data
        
        else:
            raise ArgumentError('Packets must either be instantiated from a base class with a packet_name, Packet.deserialize(), or with a header and data argument')
    
    def __bytes__(self):
        stream = WriteStream()
        self.serialize(stream)
        return bytes(stream)
    
    def serialize(self, stream):
        self.header.serialize(stream)
        if getattr(self, 'data', None) is not None:
            stream.write(self.data)
    
    @classmethod
    def deserialize(cls, stream, packet_types):
        header = LUHeader.deserialize(stream)
        packet = packet_types.get(getattr(header, 'packet_name', None), None)
        if packet is not None:
            return packet.deserialize(stream)
        else:
            return cls(header=header, data=stream.read_remaining())
        
class Action(NamedTuple):
    event: str
    handler: Callable
    priority: int
        
class Plugin(ABC):
    def __init__(self, server):
        self.server = server
    
    @abstractmethod
    def actions(self) -> List[Action]:
        return []
    
    def packets(self) -> List[Packet]:
        return []
        
def isplugin(member):
    return inspect.isclass(member) and issubclass(member, Plugin) and member is not Plugin

def get_plugins(package):
    '''
    Via https://stackoverflow.com/a/25562415/
    '''
    result = []
    if isinstance(package, str):
        package = importlib.import_module(package)
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        module = importlib.import_module(full_name)
        if is_pkg:
            result +=  get_plugins(full_name)
        else:
            for name, plugin in inspect.getmembers(module, isplugin):
                result.append(plugin)
    
    return result
