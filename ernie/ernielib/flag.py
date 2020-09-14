import sys

flags = {}


def parse(options={}):
    flags.update(options)
    argv = iter(sys.argv[1:])
    p = []
    for a in argv:
        if a.startswith("-"):
            v = None
            if "=" in a:
                k, v = tuple(a.split("=", 1))
            else:
                k = a
            i = 2 if a.startswith("--") else 1
            k = k[i:]
            if k not in flags.keys():
                return True
            c = type(flags[k])
            if c == bool:
                flags[k] = True
            else:
                if v is None:
                    try:
                        v = next(argv)
                    except StopIteration:
                        return True
                    p.append(v)
                flags[k] = c(v)
            p.append(a)
    for e in p:
        sys.argv.remove(e)
    return False
