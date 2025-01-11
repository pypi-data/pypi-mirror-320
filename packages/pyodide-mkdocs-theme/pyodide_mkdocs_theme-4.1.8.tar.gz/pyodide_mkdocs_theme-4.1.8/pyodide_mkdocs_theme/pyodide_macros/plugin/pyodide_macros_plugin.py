"""
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""


from functools import wraps
from pathlib import Path


from mkdocs.config.defaults import MkDocsConfig
from mkdocs_macros.plugin import MacrosPlugin




from ...__version__ import __version__
from ..pyodide_logger import logger
from .tools import test_cases
from .tools.macros_data import MacroData
from .maestro_base import BaseMaestro
from .maestro_files import MaestroFiles
from .maestro_meta import MaestroMeta
from .maestro_indent import MaestroIndent
from .maestro_macros import MaestroMacros
from .maestro_templates import MaestroTemplates
from .maestro_contracts import MaestroContracts
from ..macros import (
    IDEs,
    figure,
    py_script,
    qcm,
)







# NOTE: declaring the full inheritance chain isn't really needed, but it's a cool reminder... :p
class PyodideMacrosPlugin(
    MaestroContracts,
    MaestroTemplates,
    MaestroMacros,
    MaestroIndent,
    MaestroMeta,
    MaestroFiles,
    BaseMaestro,
    MacrosPlugin,    # Always last, so that other classes may trigger super methods appropriately.
):
    """
    Class centralizing all the behaviors of the different parent classes.

    This is kinda the "controller", linking all the behaviors to mkdocs machinery, while the
    parent classes hold the "somewhat self contained" behaviors.

    For reference, here are the hooks defined in the original MacrosPlugin:
        - on_serve
        - on_config
        - on_nav
        - on_page_markdown  (+ on_pre_page_macros + on_post_page_macros)
        - on_post_build     (on_post_build macros)
    """


    # Override
    def on_config(self, config:MkDocsConfig):
        # --------------------------------------------------------------
        # pylint: disable=attribute-defined-outside-init
        # Section to always apply first:

        self._conf    = config # done in MacrosPlugin, but also here because needed here or there
        self.in_serve = config.dev_addr.host in config.site_url
        self.language = config.theme['language']

        self.docs_dir_path    = Path(config.docs_dir)
        self.docs_dir_cwd_rel = self.docs_dir_path.relative_to(Path.cwd())
        # --------------------------------------------------------------

        super().on_config(config)

        MacroData.register_config(self)
        logger.info("Plugin configuration ready.")



    #--------------------------------------------------------------------------



    # Override
    def _load_modules(self):
        """ Override the super method to register the Pyodide macros at appropriate time """

        def macro_with_warning(func):
            macro = func(self)
            logged = False          # log once only per macro...

            @wraps(func)
            def wrapper(*a,**kw):
                nonlocal logged
                if not logged:
                    logged = True
                    self.warn_unmaintained(f'The macro {func.__name__!r}')
                return macro(*a,**kw)
            return wrapper

        logger.info("Register PMT macros.")
        macros = [
            IDEs.IDE,
            IDEs.IDEv,
            IDEs.IDE_tester,
            IDEs.terminal,
            IDEs.py_btn,
            IDEs.run,
            IDEs.section,
            figure.figure,
            py_script.py,
            qcm.multi_qcm,
        ]
        for func in macros:
            self.macro(func(self))
        self.macro(test_cases.Case)     # Not a macro, but needed in the jinja environment

        old_macros = []                 # Kept incase becomes useful again one day...
        for func in old_macros:
            self.macro( macro_with_warning(func) )

        super()._load_modules()



    # Override
    def _load_yaml(self):
        """
        Override the MacrosPlugin method, replacing on the fly `__builtins__.open` with a version
        handling the encoding.
        """
        # pylint: disable=multiple-statements
        src_open = open
        def open_with_utf8(*a,**kw):
            kw['encoding'] = self.load_yaml_encoding
            return src_open(*a, **kw)

        # Depending on the python version/context, the __builtins__ can be of different types
        as_dct = isinstance(__builtins__, dict)
        try:
            if as_dct:  __builtins__['open'] = open_with_utf8
            else:       __builtins__.open = open_with_utf8
            super()._load_yaml()
        finally:
            if as_dct:  __builtins__['open'] = src_open
            else:       __builtins__.open = src_open
