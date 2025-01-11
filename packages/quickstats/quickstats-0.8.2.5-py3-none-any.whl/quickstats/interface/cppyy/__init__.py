from quickstats.core.modules import require_module
require_module("cppyy")

import os
# disable precompiled header
os.environ['CLING_STANDARD_PCH'] = 'none'

import cppyy
try:
    __GLIBCXX__ = cppyy.gbl.gInterpreter.ProcessLine('__GLIBCXX__;')
except:
    __GLIBCXX__ = None

from quickstats.interface.cppyy.core import (
    cpp_define,
    addressof,
    is_null_ptr,
)
from quickstats.interface.cppyy.macros import load_macros, load_macro

load_macros()