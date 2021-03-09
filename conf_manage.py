"""
Configuration loading and saving.
"""
from pathlib import Path
import yaml


GLOBAL_LISTEN_HOST = "localhost"
GLOBAL_PUBLIC_HOST = "localhost"
GLOBAL_MAX_CONNECTIONS = 10
ENABLE_ALL = True


class SaveLoadConfig:
    """
    A class that will automatically take any non-protected variables and allow them to be saved to and loaded from disk.
    While you could subclass this (untested), you should use the decorator instead.
    """
    def __init__(self):
        self._from_disk: bool = False

    @classmethod
    def __init_subclass__(cls, path: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._data_path: str = path

    @property
    def from_disk(self) -> bool:
        return self._from_disk

    def save(self):
        self.pre_save()
        file = open(self._data_path, "w")
        yaml.safe_dump(self.to_dict(), file)
        file.close()
        self.post_save()

    def load(self):
        self.pre_load()
        file_location = self._data_path
        if Path(file_location).is_file():
            file = open(file_location, "r")
            state = yaml.safe_load(file)
            file.close()
            self._from_dict(state)
            self._from_disk = True
        self.post_load()

    def _from_dict(self, state: dict):
        for key in state:
            if key in self.__dict__:
                self.__dict__[key] = state[key]

    def to_dict(self) -> dict:
        output_dict = dict()
        for key in self.__dict__:
            if key[0] != "_":
                output_dict[key] = self.__dict__[key]
        return output_dict

    def pre_save(self):
        # Decorated class should override as needed.
        pass

    def post_save(self):
        # Decorated class should override as needed.
        pass

    def pre_load(self):
        # Decorated class should override as needed.
        pass

    def post_load(self):
        # Decorated class should override as needed.
        pass


def config_file(path: str):
    """
    Decorator that turns a given class into a config class with save and load methods.
    @param path: File path to save the class to.
    @return: Decorated class.
    """
    def decorator(cls):
        class ConfigWrapperClass(cls, SaveLoadConfig, path=path):
            def __init__(self, **kwargs):
                SaveLoadConfig.__init__(self)
                cls.__init__(self, **kwargs)
        return ConfigWrapperClass
    return decorator


class BasicConfig:
    def from_dict(self, state: dict):
        for key in state:
            if key in self.__dict__:
                self.__dict__[key] = state[key]

    def to_dict(self) -> dict:
        output_dict = dict()
        for key in self.__dict__:
            if key[0] != "_":
                output_dict[key] = self.__dict__[key]
        return output_dict


"""
From this point down, edit to add new options or change the default values.
"""


@config_file(path="config.default.yml")
class MainConfig:
    def __init__(self):
        self.globals = GlobalsConfig()
        self.cms = CMSConfig()
        self.servers = ServersConfig()

    def load(self):
        self.pre_load()
        if Path("config.yml").is_file():
            self._load_from_file("config.yml")
        elif Path("config.default.yml").is_file():
            self._load_from_file("config.default.yml")
        self.post_load()

    def _load_from_file(self, file_location: str):
        file = open(file_location, "r")
        state = yaml.safe_load(file)
        file.close()
        self._from_dict(state)
        self._from_disk = True

    def post_load(self):
        if isinstance(self.globals, dict):
            self.globals = GlobalsConfig(self.globals)
        if isinstance(self.cms, dict):
            self.cms = CMSConfig(self.cms)
        if isinstance(self.servers, dict):
            self.servers = ServersConfig(self.servers)

    def pre_save(self):
        self.globals = self.globals.to_dict()
        self.cms = self.cms.to_dict()
        self.servers = self.servers.to_dict()


class ServersConfig(BasicConfig):
    def __init__(self, state: dict = None):
        self.auth = BasicServer(1001, "auth")
        self.chat = BasicServer(2001, "chat")
        self.char = BasicServer(2003, "char")
        self.venture_explorer = BasicServer(2005, "venture_explorer")
        if state:
            self.from_dict(state)

    def __iter__(self):
        return iter([self.auth, self.chat, self.char, self.venture_explorer])

    def from_dict(self, state: dict):
        self.auth = BasicServer(1001, "auth", state["auth"])
        self.chat = BasicServer(2001, "chat", state["chat"])
        self.char = BasicServer(2003, "char", state["char"])
        self.venture_explorer = BasicServer(2005, "venture_explorer", state["venture_explorer"])

    def to_dict(self) -> dict:
        return {"auth": self.auth.to_dict(), "chat": self.chat.to_dict(), "char": self.char.to_dict(),
                "venture_explorer": self.venture_explorer.to_dict()}


class BasicServer(BasicConfig):
    def __init__(self, port: int, name: str, state: dict = None):
        self._name = name
        self.listen_port = port
        self.listen_host = GLOBAL_LISTEN_HOST
        self.public_port = port
        self.public_host = GLOBAL_PUBLIC_HOST
        self.max_connections = GLOBAL_MAX_CONNECTIONS
        self.enabled = ENABLE_ALL
        if state:
            self.from_dict(state)

    @property
    def name(self) -> str:
        return self._name


class GlobalsConfig(BasicConfig):
    def __init__(self, state: dict = None):
        self.listen_host = GLOBAL_LISTEN_HOST
        self.public_host = GLOBAL_PUBLIC_HOST
        self.max_connections = GLOBAL_MAX_CONNECTIONS
        self.enable_all = ENABLE_ALL
        if state:
            self.from_dict(state)


class CMSConfig(BasicConfig):
    def __init__(self, state: dict = None):
        self.enabled = ENABLE_ALL
        self.debug = False
        self.secret_key = "generate"
        self.listen_host = GLOBAL_LISTEN_HOST
        self.listen_port = 8080
        self.public_host = GLOBAL_PUBLIC_HOST
        self.public_port = 8080
        if state:
            self.from_dict(state)






