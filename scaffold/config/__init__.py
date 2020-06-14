import os, sys

_list = list
from ._attrs import attr, list, dict, node, root, dynamic, ref, slot, pluggable
from ._make import walk_node_attributes, walk_nodes
from ._hooks import on, before, after, run_hook, has_hook
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
    run_hook = staticmethod(run_hook)
    has_hook = staticmethod(has_hook)

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


def _parser_method_docs(parser):
    mod = parser.__module__
    mod = mod[8:] if mod.startswith("scaffold.") else mod
    class_role = ":class:`{} <{}.{}>`".format(parser.__name__, mod, parser.__name__)
    if parser.data_description:
        descr = " " + parser.data_description
    else:  # pragma: nocover
        descr = ""
    return (
        "Create a Configuration object from"
        + descr
        + " data from an object or file. The data is passed to the "
        + class_role
        + """.

        :param file: Path to a file to read the data from.
        :type file: str
        :param data: Data object to hand directly to the parser
        :type data: any
        :returns: A Configuration
        :rtype: :class:`Configuration <.conf.Configuration>`
    """
    )


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

    parser_method.__name__ = "from_" + parser._scaffold_plugin.name
    parser_method.__doc__ = _parser_method_docs(parser)
    return parser_method


for name, parser in plugins.discover("config.parsers").items():
    setattr(ConfigurationModule, "from_" + name, parser_factory(parser))
    ConfigurationModule.__all__.append("from_" + name)

ConfigurationModule.__all__ = sorted(ConfigurationModule.__all__)

sys.modules[__name__] = ConfigurationModule(__name__)
