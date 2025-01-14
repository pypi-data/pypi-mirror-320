__version__ = '2.0.0a1'
__author__ = 'veennn@proton.me'
__all__ = ['__version__', '__author__', 'rfft', 'interpolation', 'rfft_fwd', 'rwelch']

import os, platform

PATH = os.path.abspath(os.path.dirname(__file__)) + r"/normalize_rfft."
PATH += 'dll' if platform.system() == 'Windows' else 'so'
assert os.path.isfile(PATH), "Load sources error."

from ._ipp_utils import *