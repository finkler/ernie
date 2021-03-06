import sys

__all__ = ["concat", "convert", "purge", "settopo", "showres"]


def die(s, exit_status=1):
    log(s)
    sys.exit(exit_status)


def log(s, end="\n"):
    sys.stderr.write(s + end)
    sys.stderr.flush()
