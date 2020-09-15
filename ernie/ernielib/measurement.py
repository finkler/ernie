import numpy as np
import re


from ernie.ernielib import ert


class data:
    def __init__(self, name, atype="guess"):
        if name is None:
            return
        pat = re.compile("#.*")
        with open(name) as f:
            self.comment = pat.sub("", next(f)).strip()
            self.num = int(pat.sub("", next(f)))
            next(f)
            self.z = np.zeros(self.num)
            self.spacing = 0
            dx = 0
            for i in range(self.num):
                x, z = tuple([float(n) for n in next(f).split()])
                self.z[i] = z
                if i == 0:
                    dx = x
                elif i == 1:
                    self.spacing = x - dx
            self.num_data = int(pat.sub("", next(f)))
            self.rhoa = np.zeros(self.num_data)
            self.err = np.zeros(self.num_data)
            next(f)
            x = []
            for i in range(self.num_data):
                s = next(f).split()
                x.append([int(n) for n in s[:4]])
                self.rhoa[i], self.err[i] = tuple([float(n) for n in s[4:]])
            self.x = np.array(x, dtype=np.int)
            atype = atype.lower()
            if atype == "guess":
                self.atype = ert.guesstype(self.x, self.num)
            elif atype.startswith("w"):
                self.atype = ert.atype.WENNER
            elif atype.startswith("s"):
                self.atype = ert.atype.SCHLUMBERGER
            elif atype.startswith("d"):
                self.atype = ert.atype.DIPOLE
            else:
                self.atype = ert.atype.UNKNOWN

    def __str__(self):
        s = f"#{self.comment}\n"
        s += f"{self.num}# Number of electrodes\n"
        s += "# x\tz\n"
        x = np.arange(0, self.num * self.spacing, self.spacing)
        for i in range(self.num):
            s += f"{x[i]:.1f}\t{self.z[i]:.1f}\n"
        s += f"{self.num_data}# Number of data\n"
        s += "#a\tb\tm\tn\trhoa\terr\n"
        for i in range(self.num_data):
            if i == self.rhoa.size:
                break
            s += (
                "\t".join([str(n) for n in self.x[i, :]])
                + f"\t{self.rhoa[i]:.2f}\t{self.err[i]:.4f}\n"
            )
        return s

    def concat(self, other, offset):
        assert (
            self.atype == other.atype and self.spacing == other.spacing
        ), "illegal operation"
        d = data(None)
        d.atype = self.atype
        d.spacing = self.spacing
        d.comment = self.comment + " + " + other.comment
        d.num = self.num + other.num - offset
        d.z = np.zeros(d.num)
        d.z[: self.num] = self.z
        d.z[self.num :] = other.z[offset:]
        x = []
        rhoa = []
        err = []
        for arr in ert.array(self.atype, self.num):
            i = self.index(arr)
            j = other.index(np.array(arr, dtype=np.int) - self.num + offset)
            ohm = None
            e = 0
            if i:
                if j:
                    ohm = 0.5 * (self.rhoa[i] + self.rhoa[j])
                    e = np.array([self.rhoa[i], self.rhoa[j]]).std() * 100.0 / ohm
                else:
                    ohm = self.rhoa[i]
            elif j:
                ohm = self.rhoa[j]
            if ohm is None:
                continue
            x.append(arr)
            rhoa.append(ohm)
            err.append(e)
        d.err = np.array(err)
        d.rhoa = np.array(rhoa)
        d.x = np.array(x, dtype=np.int)
        d.num_data = d.x.shape[0]
        return d

    def index(self, key):
        if type(key) == np.ndarray:
            key = key.tolist()
        elif type(key) != list:
            raise TypeError
        for i in range(self.num_data):
            a = self.x[i, :].tolist()
            if a == key:
                return i
        return None


class general(data):
    def __init__(self, name):
        with open(name) as f:
            self.comment = next(f).strip()
            self.spacing = float(next(f))
            assert int(next(f)) == 11, "not a general array format"
            self.atype = int(next(f))
            next(f)
            assert int(next(f)) == 0, "needs apparent resistivity"
            self.num_data = int(next(f))
            self.rhoa = np.zeros(self.num_data)
            self.err = np.zeros(self.num_data)
            assert int(next(f)) == 2, "wrong type of x-location"
            assert int(next(f)) == 0, "I.P. data present"
            self.x = np.zeros((self.num_data, 4), dtype=np.int)
            for i in range(self.num_data):
                s = next(f).split()
                assert int(s[0]) == 4, "wrong number of electrodes"
                self.rhoa[i] = float(s[-1])
                self.x[i, :] = (
                    np.array([float(s[j]) for j in range(1, len(s) - 1, 2)])
                    / self.spacing
                    + 1
                )
            self.num = int(np.amax(self.x))
            self.z = np.zeros(self.num)
            if not next(f).startswith("0"):
                assert int(next(f)) == 2, "not a surface distance"
                assert int(next(f)) == self.num, "missing topography"
                for i in range(self.num):
                    self.z[i] = float(next(f).split()[1])


class geolog(data):
    def __init__(self, name):
        with open(name) as f:
            while True:
                self.comment = next(f).strip()
                if not self.comment.startswith("//"):
                    break
            self.spacing = float(next(f))
            self.atype = int(next(f).strip()[:1])
            self.num_data = int(next(f))
            assert int(next(f)) == 0, "invalid file"
            assert int(next(f)) == 0, "invalid file"
            self.rhoa = np.zeros(self.num_data)
            self.err = np.zeros(self.num_data)
            self.num = 0
            atomic = True
            for i in range(self.num_data):
                s = next(f).split()
                if self.atype == ert.atype.WENNER:
                    self.rhoa[i] = float(s[2])
                    self.err[i] = float(s[6])
                else:
                    self.rhoa[i] = float(s[3])
                    self.err[i] = float(s[7])
                if float(s[0]) == 0 and self.num > 0:
                    atomic = False
                if atomic:
                    self.num += 1
            self.num += 3
            x = []
            for arr in ert.array(self.atype, self.num):
                x.append(arr)
            self.x = np.array(x, dtype=np.int)
            self.z = np.zeros(self.num)
