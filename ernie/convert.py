"""convert [-g] datafile
convert geolog (or general) datafiles for usage in bert"""
import sys

from ernie.ernielib.measurement import general, geolog
from ernie.ernielib import flag


def main():
    if flag.parse({"g": False}):
        return -1

    df = general(sys.argv[1]) if flag.flags["g"] else geolog(sys.argv[1])
    print(df)
    return 0
