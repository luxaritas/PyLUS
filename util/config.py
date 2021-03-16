"""
Configuration loading and saving.
"""
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

GLOBAL_LISTEN_HOST = "localhost"
GLOBAL_PUBLIC_HOST = "localhost"
GLOBAL_MAX_CONNECTIONS = 10
ENABLE_ALL = True


class SaveLoadConfig:
    """
    A class that will automatically take any non-protected variables and allow them to be saved to and loaded from disk.
    While you could subclass this (untested), you should use the decorator instead.
    Variables prefixed with _c_ are treated as comments for the variable that comes after the prefix.
    Variables prefixed with _ are ignored.
    """
    def __init__(self):
        self._from_disk: bool = False
        self._yaml = YAML(typ="rt")
        self._yaml.indent = 4

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
        self._yaml.dump(self._build_ruamel_map(), file)
        file.close()
        self.post_save()

    def load(self):
        self.pre_load()
        file_location = self._data_path
        if Path(file_location).is_file():
            file = open(file_location, "r")
            state = self._yaml.load(file)
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

    def _build_ruamel_map(self) -> CommentedMap:
        ret = CommentedMap()
        self._recursive_build_dict(ret, self.__dict__, 0, 0)
        return ret

    def _recursive_build_dict(self, comment_map: CommentedMap, source_dict: dict, index: int, deepness: int) -> int:
        # If you find a way to sanely do this without going over it multiple times and not having it be recursive, be
        # my guest.
        cur_index = index
        for key in source_dict:
            if not key.startswith("_"):
                if isinstance(source_dict[key], dict):
                    new_map = CommentedMap()
                    comment_map.insert(cur_index, key, new_map)
                    cur_index += 1
                    cur_index = self._recursive_build_dict(new_map, source_dict[key], cur_index, deepness + 1)
                else:
                    comment_map.insert(cur_index, key, source_dict[key])
                    cur_index += 1
            # TODO: Change following if statement to use the walrus operator once 3.8+ becomes minimum.
            key_comment = source_dict.get(f"_c_{key}", None)
            if key_comment:
                comment_map.yaml_set_comment_before_after_key(key, key_comment, deepness * 4)
        return cur_index

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
            if not key.startswith("_") or key.startswith("_c_"):
                output_dict[key] = self.__dict__[key]
        return output_dict


"""
From this point down, edit the __init__'s to add new options or change the default values.
"""


@config_file(path="config.yml")
class MainConfig:
    def __init__(self):
        self.globals = GlobalsConfig()
        self._c_globals = "Defaults across all servers."
        self.cms = CMSConfig()
        self._c_cms = "Django website."
        self.servers = ServersConfig()

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

    def post_save(self):
        self.post_load()


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
        self._c_listen_host = "Default IP/domain that server instances will accept incoming connections on."
        self.public_host = GLOBAL_PUBLIC_HOST
        self._c_public_host = "Default IP/domain that will be sent to clients to connect to."
        self.max_connections = GLOBAL_MAX_CONNECTIONS
        self._c_max_connections = "Default number of maximum connections accepted per server."
        self.enable_all = ENABLE_ALL
        self._c_enable_all = "Whether all servers should be enabled by default."

        if state:
            self.from_dict(state)


class CMSConfig(BasicConfig):
    def __init__(self, state: dict = None):
        self.enabled = ENABLE_ALL
        self._c_enabled = "Whether to start the Django CMS when running the boot script"
        self.debug = False
        self._c_debug = """Whether to enable Django's debug mode (DO NOT ENABLE WHEN HOSTING PUBLICLY/OUTSIDE YOUR LAN)
When false, forever-cacheable files and compression support will be enabled in whitenoise, as
well as..?"""
        self.secret_key = "generate"
        self._c_secret_key = """Cryptographic key used by Django in cryptographic functions.
`generate` will create a new secure key whenever the server starts, which is typically optimal.
Do NOT change if you do not know how to properly generate a secure key."""
        self.listen_host = GLOBAL_LISTEN_HOST
        self._c_listen_host = "IP/domain to accept incoming connections on."
        self.listen_port = 8080
        self._c_listen_port = "Port to accept incoming connections on."
        self.public_host = GLOBAL_PUBLIC_HOST
        self._c_public_host = "IP/domain that will be sent to clients to connect to."
        self.public_port = 8080
        self._c_public_port = "Port that wil be sent to clients to connect to."

        if state:
            self.from_dict(state)
