# Copyright 2020 Visual Meaning Ltd
# This is free software licensed as GPL-3.0-or-later - see COPYING for terms.

"""Opt in debugging as a context manager."""

import contextlib
import sys


def context(should_debug):
    if should_debug:
        return Debug()
    return contextlib.nullcontext()


class Debug(contextlib.AbstractContextManager):
    """Drop into debugger if exception occurred in context."""

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            print(
                ' ! {name}: {val}'.format(name=exc_type.__name__, val=exc_val),
                file=sys.stderr)
            import pdb
            pdb.post_mortem(exc_tb)
        return False
