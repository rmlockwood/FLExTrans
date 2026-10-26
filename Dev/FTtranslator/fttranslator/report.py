"""
The report object handed to FLExTrans code: flextoolslib's own FTReporter
(it has no UI), with a handler that writes to stderr so stdout carries only
the translation.
"""

import sys

LEVELS = {0: "info", 1: "warning", 2: "error", 3: "blank"}


def make_reporter(verbose=False, stream=None):
    # Imported here: importing flextoolslib reads flextools.ini from the
    # working directory, so it has to wait for env.bootstrap().
    from flextoolslib.code.FTReport import FTReporter
    out = stream or sys.stderr
    rep = FTReporter()

    def show(message):
        kind, msg, ref = message
        if kind == rep.BLANK:
            if verbose:
                print(file=out)
            return
        if kind == rep.INFO and not verbose:
            return
        prefix = {rep.WARNING: "WARNING: ", rep.ERROR: "ERROR: "}.get(kind, "")
        print(f"{prefix}{msg}" + (f"  [{ref}]" if ref else ""), file=out)

    rep.RegisterUIHandler(show)
    return rep


def error_count(rep):
    return rep.messageCounts[rep.ERROR]


def messages(rep):
    """All messages as plain dicts, for the run record."""
    return [{"level": LEVELS[kind], "message": msg, "ref": ref}
            for kind, msg, ref in rep.messages if kind != rep.BLANK]
