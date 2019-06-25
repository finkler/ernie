def readdata(name):
    ln = []
    pat1 = re.compile(r'#.*$')
    pat2 = re.compile(r'//.*$')
    f = open(name) if name != '-' else sys.stdin
    for s in f.readlines():
        s = pat2.sub('', pat1.sub('', s)).strip()
        if s:
            ln.append(s)
    if f != sys.stdin:
        f.close()
    return ln
