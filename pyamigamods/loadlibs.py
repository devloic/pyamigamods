import ctypes
import os
from ctypes import CDLL,RTLD_GLOBAL
import cffi
songtools_shared_path=os.path.join(os.path.dirname(__file__), 'songtools.so')

def loadlibs():

    ffi = cffi.FFI()
    C = ffi.dlopen(songtools_shared_path)
    return C, ffi


