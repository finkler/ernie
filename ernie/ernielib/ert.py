import numpy as np

from enum import IntEnum


def _guesstype(arr, num, t, row):
    for i, a in enumerate(array(t, num)):
        if i == row - 1:
            if sorted(arr) == sorted(a):
                return t
        elif i == row:
            break
    return -1


def guesstype(arr, num, row=2):
    i = _guesstype(arr, num, atype.WENNER, row)
    if i > 0:
        return i
    i = _guesstype(arr, num, atype.SCHLUMBERGER, row)
    if i > 0:
        return i
    i = _guesstype(arr, num, atype.DIPOLE, row)
    if i > 0:
        return i
    return -1


class atype(IntEnum):
    WENNER = 1
    POLE = 2
    DIPOLE = 3
    WENBETA = 4
    WENGAMMA = 5
    POLEDIPOLE = 6
    SCHLUMBERGER = 7


class array:
    def __init__(self, atype, num):
        self.level = [
            self._wenner,
            self._empty,
            self._dipole,
            self._empty,
            self._empty,
            self._empty,
            self._schlumberger,
        ][atype - 1]
        self.num = num
        self.arr = np.zeros(4).astype(np.int_)

    def __iter__(self):
        self._empty()
        self.j = 0
        return self

    def __next__(self):
        if self.i == 0:
            self.level()
            self.j += 1
        else:
            self.arr += 1
        self.i -= 1
        if self.i < 0:
            raise StopIteration
        return self.arr.tolist()

    def _dipole(self):
        self.arr[0] = self.j + 4
        self.arr[1] = self.arr[0] - 1
        self.arr[2] = 2
        self.arr[3] = 1
        self.i = self.num - self.arr[0] + 1

    def _empty(self):
        self.arr[:] = 0
        self.i = 0

    def _schlumberger(self):
        self.arr[0] = self.j * 2 + 4
        self.arr[1] = 1
        self.arr[2] = self.j + 3
        self.arr[3] = self.j + 2
        self.i = self.num - 3 - self.j * 2

    def _wenner(self):
        self.arr[0] = self.j * 3 + 4
        self.arr[1] = 1
        self.arr[2] = self.j * 2 + 3
        self.arr[3] = self.j + 2
        self.i = self.num - 3 - self.j * 3
