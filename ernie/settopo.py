"""settopo [-i] [-p=profile|[-l=x1,y1,x2,y2 -elev=grid]] datafile
set topopgraphy from profile (or elevation grid) for the measurment"""
import numpy as np
import sys

from ernie.ernielib.measurement import data
from ernie.ernielib import flag


def usage():
    sys.stderr.write(
        """settopo [-i] -p=profile datafile
settopo [-i] -l=x1,y1,x2,y2 -elev=grid datafile
\t-i:    inplace edit, i.e., overwrite original datafile
\t-p:    comma separated file with profile description (x, z)
\t-l:    start and end point of profile line for the elveation grid
\t-elev: elevation grid used to defer heights of the measurements
"""
    )
    sys.exit(1)


def setfromgrid(df, seg, name):
    from ernie.ernielib import raster

    x = np.array(seg).reshape((2, 2))
    df.z = raster.extract(df.num, df.spacing, name, x)


def setfromprofile(df, name):
    x = np.arange(0, df.num * df.spacing, df.spacing)
    xy = np.loadtxt(name, delimiter=",")
    df.z = np.interp(x, xy[:, 0], xy[:, 1])


def main():
    if flag.parse({"elev": "", "i": False, "l": "", "p": ""}):
        return -1

    cond1 = flag.flags["p"]
    cond2 = flag.flags["elev"] + flag.flags["l"]
    if len(sys.argv) == 2 and sys.argv[1] == "help" or not (cond1 or cond2):
        usage()
    assert len(sys.argv) > 1, "missing datafile"
    df = data(sys.argv[1])
    if flag.flags["p"]:
        setfromprofile(df, flag.flags["p"])
    else:
        seg = [float(n) for n in flag.flags["l"].split(",")]
        setfromgrid(df, seg, flag.flags["elev"])

    if flag.flags["i"]:
        with (open(sys.argv[1]), "w") as f:
            f.write(str(df))
    else:
        print(df)
    return 0
