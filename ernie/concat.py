"""concat -offset=number datafile1 datafile2...
roll-along of two ore more measurements"""
import sys

from ernie.ernielib.measurement import data
from ernie.ernielib import flag


def usage():
    sys.stderr.write("""concat -offset=number datafile1 datafile2...
\t-offset: electrode offset
""")
    sys.exit(1)


def main():
    if flag.parse({"offset": -1}):
        return -1
    off = flag.flags["offset"]
    if len(sys.argv) == 2 and sys.argv[1] == "help" or off < 0:
        usage()
    assert len(sys.argv) > 2, "too few operands"

    df = data(sys.argv[1])
    for other in sys.argv[2:]:
        df = df.concat(data(other), off)
    print(df)
    return 0
