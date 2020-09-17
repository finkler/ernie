"""purge [-i] [-err=number] [-std=number] datafile
purge outliers from measurement"""
import numpy as np
import sys

from ernie.ernielib.measurement import data
from ernie.ernielib import flag


def usage():
    sys.stderr.write("""purge [-i] [-err=number] [-std=number] datafile
\t-i:   inplace edit, i.e., overwrite original datafile
\t-err: purge all measurements with an error greater than defined here (default: 5)
\t-std: purge all measurements that lie outside the nth-standard deviation (default: 3)
""")
    sys.exit(1)


def main():
    if flag.parse({"err": 5.0, "i": False, "std": 3.0}):
        return -1

    if len(sys.argv) == 2 and sys.argv[1] == "help":
        usage()
    assert len(sys.argv) > 1, "missing datafile"
    df = data(sys.argv[1])
    sd = df.rhoa.std() * flag.flags["std"]
    m = df.rhoa.mean()
    mask = np.logical_and(
        df.err <= flag.flags["err"],
        np.logical_and(df.rhoa >= m - sd, df.rhoa <= m + sd),
    )
    df.x = df.x[mask]
    df.rhoa = df.rhoa[mask]
    df.err = df.err[mask]
    df.num_data = np.sum(mask)
    if flag.flags["i"]:
        with open(sys.argv[1], "w") as f:
            f.write(str(df))
    else:
        print(df)
    sys.stderr.write(f"{np.sum(mask^True)} measurements purged\n")
    return 0
