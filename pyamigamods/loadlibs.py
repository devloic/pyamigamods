import ctypes
from ctypes import CDLL,RTLD_GLOBAL
import cffi
songtools_shared_path="/home/lolo/docker_apps/mvtiane/audacious-uade/build/libsongtools.so"


def loadlibs():
    #load libraries required by libsongtools.so
    #ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libstdc++.so.6", mode=RTLD_GLOBAL)
    #ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libc.so.6", mode=RTLD_GLOBAL)
    #ctypes.CDLL("/usr/local/lib/libuade.so", mode=RTLD_GLOBAL)
    #ctypes.CDLL("/usr/local/lib/libxmp.so", mode=RTLD_GLOBAL)
    #ctypes.CDLL("/usr/local/lib/libopenmpt.so", mode=RTLD_GLOBAL)
    #ctypes.CDLL("/lib/x86_64-linux-gnu/libmpg123.so", mode=RTLD_GLOBAL)

    ffi = cffi.FFI()
    C = ffi.dlopen(songtools_shared_path)
    return C, ffi


