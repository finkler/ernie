#!/usr/bin/env python3
import collections
import csv
import matplotlib.pyplot as plt
import numpy as np
import re
import subprocess
import sys


class Config:
    def __init__(self, name, num=25):
        conf = {
            'dd': self.__dipole,
            'slm': self.__schlumberger,
            'wen': self.__wenner
        }
        self.level = conf[name.lower()]
        self.num = num
        self.i = 0
        self.j = 0
        self.arr = np.zeros(4).astype(np.int_)

    def __iter__(self):
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

    def __dipole(self):
        self.arr[0] = self.j * 2 + 7
        self.arr[1] = self.j * 2 + 5
        self.arr[2] = 3
        self.arr[3] = 1
        self.i = self.num - 6 - self.j * 2

    def __schlumberger(self):
        self.arr[0] = self.j * 2 + 4
        self.arr[1] = 1
        self.arr[2] = self.j + 3
        self.arr[3] = self.j + 2
        self.i = self.num - 3 - self.j * 2

    def __wenner(self):
        self.arr[0] = self.j * 3 + 4
        self.arr[1] = 1
        self.arr[2] = self.j * 2 + 3
        self.arr[3] = self.j + 2
        self.i = self.num - 3 - self.j * 3


class Flag:
    def __init__(self, options):
        self.opts = options

    def get(self, k):
        return self.opts[k]

    def parse(self):
        argv = iter(sys.argv)
        p = []
        for a in argv:
            if a.startswith('-'):
                v = None
                if '=' in a:
                    k, v = tuple(a.split('=', 2))
                else:
                    k = a
                k = k[1:]
                if k not in self.opts.keys():
                    return True
                c = type(self.opts[k])
                if c == bool:
                    self.opts[k] ^= True
                else:
                    if v is None:
                        v = next(argv)
                        p.append(v)
                    self.opts[k] = c(v)
                p.append(a)
        for e in p:
            sys.argv.remove(e)
        return False


def __c_concat() -> int:
    flags = Flag({'c': '', 'elev': '', 'err': 3.0, 'o': 0})
    if flags.parse() or flags.get('c') == '' or len(sys.argv) < 2:
        usage()

    def concatenateBuffer(buf1, buf2) -> list:
        offset = flags.get('o')
        name = flags.get('c')
        elev = flags.get('elev')
        err = flags.get('err')
        buf = []

        n1 = int(buf1[0])
        n2 = int(buf2[0])
        sp = int(float(buf1[2].split()[0]) - float(buf1[1].split()[0]))
        log('Concatenate: {} m spacing {} and electrodes offset'.format(
            sp, offset))
        n = n1 + offset
        buf.append(str(n))
        x, y = coords(elev, n, sp)
        for i in range(x.size):
            buf.append('{:.1f}\t{:.1f}'.format(x[i], y[i]))

        nd1 = int(buf1[n1 + 1])
        nd2 = int(buf2[n2 + 1])
        d1 = np.fromstring(
            '\n'.join(buf1[n1 + 2:n1 + nd1 + 2]), sep='\t').reshape((-1, 5))
        d2 = np.fromstring(
            '\n'.join(buf2[n2 + 2:n2 + nd2 + 2]), sep='\t').reshape((-1, 5))
        d2[:, :4] += n1 - n2 + offset

        conf = Config(name, n)
        df = []
        for c in conf:
            a = frozenset(c)
            r1 = None
            r2 = None
            for d in d1:
                b = d[:4].astype(np.int_).tolist()
                if len(a.intersection(b)) == len(b):
                    r1 = d[4]
                    break
            for d in d2:
                b = d[:4].astype(np.int_).tolist()
                if len(a.intersection(b)) == len(b):
                    r2 = d[4]
                    break
            ohm = None
            if r1:
                if r2:
                    ohm = .5 * (r1 + r2)
                    var = np.array([r1, r2]).std() * 100. / ohm
                    if var > err:
                        ohm = None
                        log('Collision: discarded with {:.2f} % deviation'.
                            format(var))
                else:
                    ohm = r1
            elif r2:
                ohm = r2
            if ohm:
                df.append('{:4d}\t{:4d}\t{:4d}\t{:4d}\t{:.2f}'.format(*c, ohm))

        buf.append(str(len(df)))
        return buf + df

    buf = readdata(sys.argv[0])
    for i in range(1, len(sys.argv)):
        buf = concatenateBuffer(buf, readdata(sys.argv[i]))
    i = int(buf[0])
    buf[0] += '# Number of electrodes'
    buf.insert(1, '#x\tz')
    buf[i + 2] += '# Number of data'
    buf.insert(i + 3, '#a\t b\t m\t n\trhoa')
    print('\n'.join(buf))
    return 0


def __c_convert() -> int:
    flags = Flag({'elev': '', 'n': 25, 'err': 3.0})
    if flags.parse() or len(sys.argv) != 1:
        usage()

    log('Convert: {} with {} electrodes - deviation error {} %'.format(
        sys.argv[0], flags.get('n'), flags.get('err')))
    buf = readdata(sys.argv[0])
    print('# ' + buf[0])
    num = flags.get('n')
    print('{}# Number of electrodes'.format(num))

    suff = sys.argv[0].split('.')[-1]
    conf = Config(suff, num)

    space = float(buf[1])
    x, y = coords(flags.get('elev'), num, space)
    print('#x\tz')
    for i in range(num):
        print('{:.1f}\t{:.1f}'.format(x[i], y[i]))

    num = int(buf[3])
    df = ''
    i = 3 if suff != 'wen' else 2
    s = iter(buf[6:])
    for c in conf:
        row = next(s).split()
        e = float(row[i + 4])
        if e > flags.get('err'):
            num -= 1
            log('Measurement discarded with {} % deviation'.format(e))
            continue
        c += [float(row[i])]
        df += '{:4d}\t{:4d}\t{:4d}\t{:4d}\t{:.2f}\n'.format(*c)

    print('{}# Number of data'.format(num))
    print('#a\t b\t m\t n\trhoa')
    print(df)
    return 0


def __c_mergepdf():
    if len(sys.argv) < 2:
        usage()

    cmd = [
        'gs', '-dBATCH', '-dNOPAUSE', '-q', '-sDEVICE=pdfwrite',
        '-sOutputFile=result.pdf'
    ] + argv
    p = subprocess.run(cmd)
    return p.returncode


def __c_showres() -> int:
    flags = Flag({'q': '25,75', 'ohm': ''})
    if flags.parse():
        usage()

    if flags.get('ohm'):
        i = [float(n) for n in flags.get('ohm').split(',')]
    else:
        q = [float(n) for n in flags.get('q').split(',')]
        a = np.loadtxt(sys.argv[0])
        i = np.percentile(a, q)
    res = []
    with open('/home/thk32is/docs/resistivity.csv') as f:
        for row in csv.reader(f):
            try:
                a = float(row[2])
                b = float(row[3])
                if i[-1] >= a and i[0] < b:
                    res.append([row[0], (a, b)])
            except ValueError:
                a = float(row[4])
                if i[0] < a and i[-1] > a:
                    res.append([row[0], (a, a)])
    n = 0
    for r in res:
        d = len(r[0])
        if d > n:
            n = d
    print('-' * (25 + n))
    print('Nr | {:{n}} | Range'.format('Material', n=n))
    print('-' * (25 + n))
    for i, r in enumerate(res):
        nam = r[0]
        a, b = r[1]
        print('{:2d} | {:{n}} | {:.1e} - {:.1e}'.format(i + 1, nam, a, b, n=n))
    print('-' * (25 + n))
    return 0


def coords(name, n, d):
    x = np.arange(0, n * d, d)
    if not name:
        return x, np.zeros(x.size)
    xy = np.loadtxt(name, delimiter=',')
    return x, np.interp(x, xy[:, 0], xy[:, 1])


def log(s):
    sys.stderr.write(s + '\n')
    sys.stderr.flush()


def readdata(name):
    ln = []
    pat1 = re.compile(r'#.*$')
    pat2 = re.compile(r'//.*$')
    f = open(name) if name != '-' else sys.stdin
    for s in f.readlines():
        s = pat2.sub('', pat1.sub('', s)).strip()
        if s:
            ln.append(s)
    if f != sys.stdin:
        f.close()
    return ln


def usage():
    sys.stderr.write(
        'usage: ernie command\n' + 'commands are:\n' +
        '\tconcat -c=name -o=num datafile1 datafile2...\n' +
        '\t\t--- concatenates multiple arrays into one (roll-along)\n' +
        '\tconvert [-elev=name] [-err=num] [-n=num] datafile\n' +
        '\t\t--- converts GeoTom datafile into BERT format\n' +
        '\tmergepdf pdf1 pdf2...\n' +
        '\t\t--- merges multiple pdfs into a single pdf\n' +
        '\tshowres [resistivity]\n' + '\t\t--- shows resisitivity values\n')
    sys.exit(1)


if __name__ == '__main__':
    sys.argv.pop(0)
    if len(sys.argv) < 1:
        usage()

    rc = {}
    key, val = None, None
    for key, val in locals().items():
        if callable(val) and val.__module__ == __name__ \
                and key.startswith('__c_'):
            rc[key[4:]] = val
    cmd = sys.argv.pop(0)
    if cmd not in rc.keys():
        usage()
    sys.exit(rc[cmd]())
