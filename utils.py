import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.sterr, **kwargs)
