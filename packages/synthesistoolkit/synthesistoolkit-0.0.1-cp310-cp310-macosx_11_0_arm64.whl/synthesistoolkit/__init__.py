import os
import importlib
import importlib.resources
from ._pystk_impl import *

with importlib.resources.path('synthesistoolkit', 'rawwaves') as fspath:
    set_rawwave_path(str(fspath))
