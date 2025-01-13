import sys
from os.path import isdir
from importlib import invalidate_caches
import importlib.util
from importlib.abc import SourceLoader
from importlib.machinery import FileFinder
import json
from typing import Union
import warnings

try:
    import pythonmonkey as pm
except ImportError:
    warnings.warn("""Unable to load pythonmonkey. Loader will not work, but you
        can still use JsCode""")


class JsCode:
    """Wrapper around Javascript code."""

    def __init__(self, js_code: Union[str, "JsCode"]):
        if isinstance(js_code, JsCode):
            self.js_code: str = js_code.js_code
        else:
            self.js_code = js_code

    def __str__(self):
        return self.js_code


class JavascriptLoader(SourceLoader):
    """A module loader hook that will allow loading of Javascript modules"""
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path

    def get_filename(self, fullname):
        return self.path

    def get_data(self, filename):
        """exec_module is already defined for us, we just have to provide a way
        of getting the source code of the module"""

        module = pm.require(filename)
        symbols = pm.eval("(module) => { return Object.keys(module) }")(module)
        toString = pm.eval("(module, name) => module[name].toString()")
        lines = ["from js_loader import JsCode"]
        for symbol in symbols:
            body = toString(module, symbol)
            lines.append(f'{symbol} = JsCode("""\n{body}\n""")')
        return "\n".join(lines)


class JsCodeEncoder(json.JSONEncoder):
    """This will wrap javascript code inside a json string."""
    prefix = "::JSCODE::"
    postfix = "::JSCODE::"

    def default(self, o):
        if isinstance(o, JsCode):
            return self.prefix + str(o) + self.postfix
        else:
            return json.JSONEncoder.default(self, o)


def install_js_loader():
    """Install the Javascript Loader hook"""
    loader_details = JavascriptLoader, [".js"]
    # insert the path hook after other path hooks
    sys.path_hooks.insert(-1, FileFinder.path_hook(loader_details))
    # clear any loaders that might already be in use by the FileFinder
    sys.path_importer_cache.clear()
    invalidate_caches()
