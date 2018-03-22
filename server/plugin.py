from abc import ABC, abstractmethod
import inspect, importlib, pkgutil

class Plugin(ABC):
    def __init__(self, server):
        self.server = server
    
    @abstractmethod
    def actions(self):
        '''
        Returns dictionary of handlers the plugin consumes in the format:
        {
            'event_name': function
        }
        '''
        return {}
      
    def events(self):
        '''
        Returns a tuple or list of events the plugin raises
        '''
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
