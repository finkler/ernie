"""convert [-g] datafile
convert geolog (or general) datafiles for usage in bert"""
import sys

from ernie.ernielib.measurement import general, geolog
from ernie.ernielib import flag


def usage():
    sys.stderr.write("""convert [-g] datafile
\t-g: general data file format
""")
    sys.exit(1)


def main():
    if flag.parse({"g": False}):
        return -1

    if len(sys.argv) == 2 and sys.argv[1] == "help":
        usage()
    assert len(sys.argv) > 1, "missing datafile"
    df = general(sys.argv[1]) if flag.flags["g"] else geolog(sys.argv[1])
    print(df)
    return 0
