import ctypes
from ctypes import wintypes


ERROR_ALREADY_EXISTS = 183

_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_create_mutex = _kernel32.CreateMutexW
_create_mutex.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
_create_mutex.restype = wintypes.HANDLE
_close_handle = _kernel32.CloseHandle
_close_handle.argtypes = [wintypes.HANDLE]
_close_handle.restype = wintypes.BOOL


class SingleInstanceLock:
    def __init__(self, name):
        self.name = name
        self.handle = None

    def acquire(self):
        handle = _create_mutex(None, False, self.name)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())

        if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
            _close_handle(handle)
            return False

        self.handle = handle
        return True

    def release(self):
        if self.handle is not None:
            _close_handle(self.handle)
            self.handle = None
