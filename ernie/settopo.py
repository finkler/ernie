"""settopo [-i] [-p=profile|[-o=x,y -elev=grid]] datafile
set topopgraphy from profile (or elevation grid) for the measurment"""
import numpy as np
import sys

from ernie.ernielib.measurement import data
from ernie.ernielib import flag


def setfromgrid(df, origin, name):
    pass


def setfromprofile(df, name):
    x = np.arange(0, df.num * df.spacing, df.spacing)
    xy = np.loadtxt(name, delimiter=",")
    df.z = np.interp(x, xy[:, 0], xy[:, 1])


def main():
    if flag.parse({"elev": "", "i": False, "o": "", "p": ""}):
        return -1

    df = data(sys.argv[1])
    if flag.flags["p"]:
        setfromprofile(df, flag.flags["p"])
    else:
        o = tuple([float(n) for n in flag.flags["o"].split(",")])
        setfromgrid(df, o, flag.flags["elev"])

    if flag.flags["i"]:
        with (open(sys.argv[1]), "w") as f:
            f.write(str(df))
    else:
        print(df)
    return 0
