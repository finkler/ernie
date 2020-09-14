"""concat datafile1 datafile2...
roll-along of two ore more measurements"""
import sys

from ernie.ernielib.measurement import data
from ernie.ernielib import flag


def main():
    if flag.parse({"offset": 0, "type": ""}):
        return -1

    off = flag.flags["offset"]
    df = data(sys.argv[1])
    for other in sys.argv[2:]:
        df = df.concat(data(other), off)
    print(df)
    return 0
