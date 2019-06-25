"""convert [-elev=name] [-err=num] [-n=num] datafile
converts GeoTom datafile into BERT format"""

from ernie import *
from ernie.ernielib import flag

def main():
    flag.flags = {'elev': '', 'n': 25, 'err': 3.0}
    if flag.parse() or len(sys.argv) != 1:
        return -1

    log('Convert: {} with {} electrodes - deviation error {} %'.format(
        sys.argv[0], flag.flags['n'], flag.flags['err']))
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
