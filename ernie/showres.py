"""showres [-q=from,to|-ohm=from,to] [-plot] [resfile]
show materials that fall into the given resistivity
percentile (or absolute) range"""
import csv
import numpy as np
import sys

from ernie.ernielib import flag

database = "/home/thk32is/docs/resistivity.csv"


def printgui(res, lim):
    import matplotlib.pyplot as plt

    y = []
    x0 = []
    x1 = []
    colors = []
    for r in res:
        y.append(r[0])
        a, b = r[1]
        x0.append(a)
        x1.append(b)
        colors.append("g" if r[2] else "b")

    plt.rcdefaults()
    fig, ax = plt.subplots()

    y_pos = np.arange(len(y))

    ax.set_xscale("log")
    ax.barh(y_pos, x1, left=x0, tick_label=y, align="center", color=colors)
    ax.invert_yaxis()
    ax.set_xlabel("Resistance [Ohm]")
    ax.set_axisbelow(True)
    ax.axvspan(lim[0], lim[1], alpha=0.5, color="yellow")

    plt.grid(b=True, axis="y")
    plt.show()


def printtxt(res, lim):
    res = list(filter(lambda r: r[2], res))
    n = 0
    for r in res:
        d = len(r[0])
        if d > n:
            n = d
    print("-" * (25 + n))
    print("Nr | {:{n}} | Range".format("Material", n=n))
    print("-" * (25 + n))
    for i, r in enumerate(res):
        nam = r[0]
        a, b = r[1]
        print("{:2d} | {:{n}} | {:.1e} - {:.1e}".format(i + 1, nam, a, b, n=n))
    print("-" * (25 + n))


def main():
    if flag.parse({"plot": False, "q": "25,75", "ohm": ""}):
        return -1

    if flag.flags["ohm"]:
        i = [float(n) for n in flag.flags["ohm"].split(",")]
    else:
        q = [float(n) for n in flag.flags["q"].split(",")]
        nam = sys.argv[1] if len(sys.argv) > 1 else "resistivity.vector"
        a = np.loadtxt(nam)
        i = np.percentile(a, q)
    res = []
    with open(database) as f:
        for row in csv.reader(f):
            try:
                a = float(row[2])
                b = float(row[3])
                mark = i[-1] >= a and i[0] < b
                res.append([row[0], (a, b), mark])
            except ValueError:
                continue
                a = float(row[4])
                b = 0.5 * (i[0] + i[-1])
                if a > b:
                    temp = b
                    b = a
                    a = temp
                res.append([row[0], (a, b)])
    if flag.flags["plot"]:
        printgui(res, i)
    else:
        printtxt(res, i)
    return 0
