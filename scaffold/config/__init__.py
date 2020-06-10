import os, sys

_list = list
from ._attrs import attr, list, dict, node, root, dynamic, ref, slot, pluggable
from ._make import walk_node_attributes, walk_nodes
from ._hooks import on, before, after
from .. import plugins


_path = __path__


class ConfigurationModule:
    def __init__(self, name):
        self.__name__ = name

    attr = staticmethod(attr)
    list = staticmethod(list)
    dict = staticmethod(dict)
    ref = staticmethod(ref)
    slot = staticmethod(slot)

    node = staticmethod(node)
    root = staticmethod(root)
    dynamic = staticmethod(dynamic)
    pluggable = staticmethod(pluggable)

    walk_node_attributes = staticmethod(walk_node_attributes)
    walk_nodes = staticmethod(walk_nodes)
    on = staticmethod(on)
    after = staticmethod(after)
    before = staticmethod(before)

    # The __path__ attribute needs to be retained to mark this module as a package
    __path__ = _path

    # Load the Configuration class on demand, not on import, to avoid circular
    # dependencies.

    @property
    def Configuration(self):
        if not hasattr(self, "_cfg_cls"):
            from ._config import Configuration

            self._cfg_cls = Configuration
        return self._cfg_cls

    __all__ = _list(vars().keys() - {"__init__", "__qualname__", "__module__"})


def parser_factory(parser):
    def parser_method(self, file=None, data=None):
        if file is not None:
            file = os.path.abspath(file)
            with open(file, "r") as f:
                data = f.read()
        tree, meta = parser().parse(data, path=file)
        conf = self.Configuration.__cast__(tree, None)
        conf._parser = parser._scaffold_plugin.name
        conf._meta = meta
        conf._file = file
        return conf

    return parser_method


for name, parser in plugins.discover("config.parsers").items():
    setattr(ConfigurationModule, "from_" + name, parser_factory(parser))
    ConfigurationModule.__all__.append("from_" + name)

sys.modules[__name__] = ConfigurationModule(__name__)
