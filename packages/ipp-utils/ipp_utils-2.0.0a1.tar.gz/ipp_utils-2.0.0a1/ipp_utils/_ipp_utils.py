import numpy as np
import array
from typing import Optional, Callable
from scipy import signal
from ctypes import Structure, c_float, c_int, c_char_p, c_void_p, POINTER, byref, CDLL
from . import PATH
from enum import IntEnum

__all__ = ['rfft', 'interpolation', 'rfft_fwd', 'rwelch']


class nDsts(Structure):
    _fields_ = [("point", POINTER(c_float)), ("x", c_int), ("y", c_int), ("status", c_int)]


class ndata(Structure):
    _fields_ = [("point", POINTER(c_float)), ("x", c_int), ("y", c_int), ("status", c_int), ("buffer", c_void_p)]


class WIN_TYPE(IntEnum):
    CUSTOM = 0
    HANN = 1
    HAMMING = 2
    BLACKMAN = 3
    BARTLETT = 4
    KAISER = 5
    BLACKMANHARRIS = 6


class WELCH_TYPE(IntEnum):
    WATTS = 0,
    DBFS = 1,
    DBV = 1,
    DBUV = 2,
    DBW = 3,
    DBM = 4,
    WATTS_HZ = 5,
    DBFS_HZ = 6,
    DBW_HZ = 7,
    DBM_HZ = 8


class FFT_TYPE(IntEnum):
    LOGARITHMIC = 0,
    LINEAR = 1


class interpolation():
    r"""
        interpolation

        Parameters
        ----------
        data_array : array.array
            1D array data.
        slice : int
            Number of slices between two numbers.

        Returns
        -------
        : np.ndarray
    """
    __dll = CDLL(PATH)
    __ret = None

    def __init__(self, data_array: array.array, slice: int = 3) -> None:
        assert len(data_array) >= 8, "Invalid args data_array."
        assert 64 >= slice >= 3, "Invalid args slice."
        self.data_array = data_array
        self.slice = int(slice)

    def __enter__(self) -> np.ndarray:
        Src = np.ctypeslib.as_ctypes(np.array(self.data_array).astype(np.float32))
        self.__dll.interpolation.restype = POINTER(nDsts)
        self.__ret = self.__dll.interpolation(byref(Src), len(Src), self.slice)
        if self.__ret.contents.status != 0:
            raise BaseException(self.__ret.contents.status)
        ret = np.ctypeslib.as_array(self.__ret.contents.point, shape=(self.__ret.contents.x, self.__ret.contents.y)).copy()
        return ret

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (self.__ret):
            self.__dll.Ipp32fs_free.restype = c_void_p
            self.__dll.Ipp32fs_free.argtypes = [POINTER(nDsts)]
            self.__dll.Ipp32fs_free(self.__ret)
            self.__ret = None
        if exc_type and issubclass(exc_type, BaseException):
            print(exc_tb.tb_lineno, exc_val.args, exc_tb.tb_frame.f_code.co_filename)


class rfft():
    r"""
        rfft

        Parameters
        ----------
        data_array : array.array
            1D array data.
        NFFT : int
            FFT window size in [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536].
        window_type: str
            FFT window type in ['hann', 'hamming', 'blackman', 'blackmanharris', 'bartlett'].
        ret_type: str
            Spectral type in ['logarithmic', 'linear']
        overlap: int
            The amount of overlap, value >= -1 and < NFFT, -1 means automatic sliding window.

        Returns
        -------
        : np.ndarray
    """
    __dll = CDLL(PATH)
    __ret = None

    def __init__(self, data_array: array.array, NFFT: int = 128, window_type: str = 'hann', ret_type: str = 'logarithmic', overlap: int = -1) -> None:
        assert len(data_array) >= 128, "Invalid args data_array."
        assert NFFT in [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536], "Invalid args NFFT."
        assert window_type in ['hann', 'hamming', 'blackman', 'blackmanharris', 'bartlett'], "Invalid args window_type."
        assert ret_type in ['logarithmic', 'linear'], "Invalid args ret_type."
        assert isinstance(overlap, int) and overlap >= -1 and overlap < NFFT
        self.NFFT = NFFT
        self.window_type = window_type
        self.ret_type = c_char_p(ret_type.encode())
        self.data_array = data_array
        self.overlap = overlap

    def __enter__(self) -> np.ndarray:
        Src = np.ctypeslib.as_ctypes(np.array(self.data_array).astype(np.float32))
        Win = np.ctypeslib.as_ctypes(np.append(signal.get_window(self.window_type, int(self.NFFT - 1)), [0.]).astype(np.float32))
        if self.overlap == -1:
            self.overlap = 0
            while len(self.data_array) / (self.NFFT - self.overlap) < 1920 and self.overlap < (self.NFFT - 1):
                self.overlap += 1
        self.__dll.normalize_rfft.restype = POINTER(nDsts)
        self.__ret = self.__dll.normalize_rfft(byref(Src), byref(Win), self.NFFT, len(Src), self.overlap, self.ret_type)
        if self.__ret.contents.status != 0:
            raise BaseException(self.__ret.contents.status)
        ret = np.ctypeslib.as_array(self.__ret.contents.point, shape=(self.__ret.contents.x, self.__ret.contents.y))[:, :-1].copy()
        return ret

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (self.__ret):
            self.__dll.Ipp32fs_free.restype = c_void_p
            self.__dll.Ipp32fs_free.argtypes = [POINTER(nDsts)]
            self.__dll.Ipp32fs_free(self.__ret)
            self.__ret = None
        if exc_type and issubclass(exc_type, BaseException):
            print(exc_tb.tb_lineno, exc_val.args, exc_tb.tb_frame.f_code.co_filename)


class rfft_fwd():
    r"""
        rfft_fwd

        Parameters
        ----------
        src_len : int
            The length of the original data for each calculation.
        win_type: str
            FFT window type in ['hann', 'hamming', 'blackman', 'blackmanharris', 'bartlett', 'kaiser', 'custom'].
        NFFT : int
            FFT window size in [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536].
        overlap: int
            The amount of overlap, value >= -1 and < NFFT, -1 means automatic sliding window.
        win : array.array
            1D array window data. Required when the win_type parameter is 'custom'.

        Returns
        -------
        : np.ndarray
    """
    __dll = CDLL(PATH)
    __ret = None

    def __init__(self, src_len: int, win_type: str = 'hann', NFFT: int = 128, overlap: int = -1, win: Optional[array.array] = None) -> None:
        assert isinstance(src_len, int) and src_len >= 128, "Invalid args src_len."
        assert NFFT in [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536], "Invalid args NFFT."
        assert win_type in ['hann', 'hamming', 'blackman', 'blackmanharris', 'bartlett', 'kaiser', 'custom'], "Invalid args win_type."
        if win_type == 'custom':
            assert len(win) == NFFT, "Invalid args win."
        assert isinstance(overlap, int) and overlap >= -1 and overlap < NFFT
        self.src_len = src_len
        if overlap == -1:
            overlap = 0
            while self.src_len / (NFFT - overlap) < 1920 and overlap < (NFFT - 1):
                overlap += 1
        self.__dll.nor_rfft_init.restype = POINTER(ndata)
        self.__dll.nor_rfft.restype = c_int
        self.__dll.Ipp32fs_free.restype = c_void_p
        self.__dll.Ipp32fs_free.argtypes = [POINTER(ndata)]
        if win_type == "custom":
            Win = np.ctypeslib.as_ctypes(np.array(win).astype(np.float32))
            self.__buf = self.__dll.nor_rfft_init(WIN_TYPE.CUSTOM, NFFT, self.src_len, overlap, byref(Win))
        if win_type in ['blackmanharris']:
            Win = np.ctypeslib.as_ctypes(np.append(signal.get_window(win_type, int(NFFT - 1)), [0.]).astype(np.float32))
            self.__buf = self.__dll.nor_rfft_init(WIN_TYPE.CUSTOM, NFFT, self.src_len, overlap, byref(Win))
        else:
            self.__buf = self.__dll.nor_rfft_init(WIN_TYPE[win_type.upper()].value, NFFT, self.src_len, overlap, None)

    def __enter__(self) -> Callable[[array.array, str], np.ndarray]:
        return self.__buffer

    def __buffer(self, data_array: array.array, ret_type: str = 'logarithmic') -> np.ndarray:
        r"""
            __buffer

            Parameters
            ----------
            data_array : array.array
                1D array data.
            ret_type: str
                Spectral type in ['logarithmic', 'linear']

            Returns
            -------
            : np.ndarray
        """

        assert ret_type in ['logarithmic', 'linear'], "Invalid args ret_type."
        assert self.src_len == len(data_array), "Invalid args data_array length."
        Src = np.ctypeslib.as_ctypes(np.array(data_array).astype(np.float32))

        r_int = self.__dll.nor_rfft(byref(Src), self.__buf, FFT_TYPE[ret_type.upper()].value)
        if r_int != 0:
            raise BaseException(self.__buf.contents.status)
        self.__ret = np.ctypeslib.as_array(self.__buf.contents.point, shape=(self.__buf.contents.x, self.__buf.contents.y))[:, :-1].copy()
        return self.__ret

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (self.__buf):
            self.__dll.Ipp32fs_free(self.__buf)
            self.__buf = None
        if exc_type and issubclass(exc_type, BaseException):
            print(exc_tb.tb_lineno, exc_val.args, exc_tb.tb_frame.f_code.co_filename)


class rwelch():
    r"""
        Estimate power spectral density using Welch's method.

        Parameters
        ----------
        data_array : array.array
            1D array data.
        fs : int
            The sample rate of the input in Hz.
        win_type: str
            FFT window type in ['hann', 'hamming', 'blackman', 'blackmanharris', 'bartlett', 'kaiser', 'custom'].
        NFFT : int
            FFT window size in [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536].
        overlap: int
            The amount of overlap, value >= -1 and < NFFT, -1 means automatic sliding window.
        win : array.array
            1D array window data. Required when the win_type parameter is 'custom'.

        Returns
        -------
        : np.ndarray
    """
    __dll = CDLL(PATH)
    __ret = None

    def __init__(self, data_array: array.array, fs: int, win_type: str = 'hann', NFFT: int = 128, overlap: int = -1, win: Optional[array.array] = None) -> None:
        assert len(data_array) >= 128, "Invalid args data_array."
        assert isinstance(fs, int) and fs > 0, "Invalid args fs."
        assert NFFT in [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536], "Invalid args NFFT."
        assert win_type in ['hann', 'hamming', 'blackman', 'blackmanharris', 'bartlett', 'kaiser', 'custom'], "Invalid args win_type."
        if win_type == 'custom':
            assert len(win) == NFFT, "Invalid args win."
        assert isinstance(overlap, int) and overlap >= -1 and overlap < NFFT
        self.src_len = len(data_array)
        if overlap == -1:
            overlap = 0
            while self.src_len / (NFFT - overlap) < 1920 and overlap < (NFFT - 1):
                overlap += 1
        self.__dll.rwelch_init.restype = POINTER(ndata)
        self.__dll.rwelch.restype = c_int
        self.__dll.Ipp32fs_free.restype = c_void_p
        self.__dll.Ipp32fs_free.argtypes = [POINTER(ndata)]
        Src = np.ctypeslib.as_ctypes(np.array(data_array).astype(np.float32))
        if win_type == "custom":
            Win = np.ctypeslib.as_ctypes(np.array(win).astype(np.float32))
            self.__buf = self.__dll.rwelch_init(byref(Src), WIN_TYPE.CUSTOM, NFFT, self.src_len, overlap, byref(Win), fs)
        if win_type in ['blackmanharris']:
            Win = np.ctypeslib.as_ctypes(np.append(signal.get_window(win_type, int(NFFT - 1)), [0.]).astype(np.float32), fs)
            self.__buf = self.__dll.rwelch_init(byref(Src), WIN_TYPE.CUSTOM, NFFT, self.src_len, overlap, byref(Win), fs)
        else:
            self.__buf = self.__dll.rwelch_init(byref(Src), WIN_TYPE[win_type.upper()].value, NFFT, self.src_len, overlap, None, fs)

    def __enter__(self) -> Callable[[float, str], np.ndarray]:
        return self.__buffer

    def __buffer(self, load: float, ret_type: str = 'logarithmic') -> np.ndarray:
        r"""
            __buffer

            Parameters
            ----------
            load: float
                Reference load to compute power levels(Ω), between 1.0 and 300.0.
            ret_type: str
                Spectral type in ['Watts', 'dBFS', 'dBV', 'dBuV', 'dBW', 'dbm', 'Watts_Hz', 'dBFS_Hz', 'dBW_Hz','dBm_Hz']

            Returns
            -------
            : np.ndarray
        """

        assert ret_type in ['Watts', 'dBFS', 'dBV', 'dBuV', 'dBW', 'dbm', 'Watts_Hz', 'dBFS_Hz', 'dBW_Hz', 'dBm_Hz'], "Invalid args ret_type."
        assert 1.0 <= load <= 300.0, "Invalid args load."
        r_int = self.__dll.rwelch(self.__buf, WELCH_TYPE[ret_type.upper()].value, c_float(load))
        if r_int != 0:
            raise BaseException(self.__buf.contents.status)
        self.__ret = np.ctypeslib.as_array(self.__buf.contents.point, shape=(1, self.__buf.contents.y))[:, :-1].copy()
        return self.__ret

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (self.__buf):
            self.__dll.Ipp32fs_free(self.__buf)
            self.__buf = None
        if exc_type and issubclass(exc_type, BaseException):
            print(exc_tb.tb_lineno, exc_val.args, exc_tb.tb_frame.f_code.co_filename)
