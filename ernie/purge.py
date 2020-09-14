"""purge [-i] [-err=number] [-std=number] datafile
purge outliers from measurement"""
import numpy as np
import sys

from ernie.ernielib.measurement import data
from ernie.ernielib import flag


def main():
    if flag.parse({"err": 0.0, "i": False, "std": 1.0}):
        return -1

    err = np.abs(flag.flags["err"])
    df = data(sys.argv[1])
    sd = df.err.std() * flag.flags["std"] if err == 0 else err
    mask = df.err <= sd
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
    print(df.atype)
    return 0
