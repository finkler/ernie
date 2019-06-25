from enum import IntEnum


class Config(IntEnum):
    DIPOLE = 0
    SCHLUMBERGER = 1
    WENNER = 2


class Layout:
    def __init__(self, cfg, num=25):
        self.level = [_dipole, _schlumberger, _wenner][cfg]
        self.num = num
        self.arr = np.zeros(4).astype(np.int_)

    def __iter__(self):
        self.arr = 0
        self.i = 0
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
        self.arr[0] = self.j * 2 + 7
        self.arr[1] = self.j * 2 + 5
        self.arr[2] = 3
        self.arr[3] = 1
        self.i = self.num - 6 - self.j * 2

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
