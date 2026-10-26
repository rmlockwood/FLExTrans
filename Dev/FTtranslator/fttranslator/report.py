#
#   fttranslator/report
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Makes the report object handed to FLExTrans code, writing its messages to stderr.
#
#   OVERVIEW (AI generated, then edited)
#
#   FLExTrans code reports through the object FlexTools passes it (report.Info, report.Warning, report.Error, report.Blank). FTtranslator uses flextoolslib's own FTReporter, which has no UI of
#   its own, and registers a handler that prints to stderr. stdout is kept for the translation alone, so it can be piped.
#
#   WHAT IS SHOWN
#
#   Warnings and errors are always printed. Info messages and blank lines are printed only with --verbose, since FLExTrans is chatty and the user mostly wants the translation and the words
#   that failed. Every message is still kept in the reporter, and messages() turns them into the plain dictionaries saved in the run record.
#
#   IMPORT ORDER
#
#   FTReporter is imported inside makeReporter(), not at the top, because importing flextoolslib reads flextools.ini from the working directory and so has to wait for env.bootstrap(). It lives
#   in flextoolslib.code.FTReport and is not exported from flextoolslib itself.
#
#   CODE STRUCTURE
#
#   makeReporter() builds the reporter and its stderr handler. errorCount() is what pipeline.run() uses to notice that a step reported an error, and messages() is what it saves in the run record.
#

import sys

# FTReporter's message kinds, as the words used in the run record
LEVELS = {0: "info", 1: "warning", 2: "error", 3: "blank"}

def makeReporter(verbose=False, stream=None):
    '''Return an FTReporter that prints warnings and errors (and, when verbose, everything) to stream, which defaults to stderr.'''

    # Imported here: importing flextoolslib reads flextools.ini from the working directory, so it has to wait for env.bootstrap()
    from flextoolslib.code.FTReport import FTReporter

    out = stream or sys.stderr
    reporter = FTReporter()

    def show(message):

        kind, text, reference = message

        if kind == reporter.BLANK:

            if verbose:

                print(file=out)

            return

        if kind == reporter.INFO and not verbose:

            return

        prefix = {reporter.WARNING: "WARNING: ", reporter.ERROR: "ERROR: "}.get(kind, "")
        print(f"{prefix}{text}" + (f"  [{reference}]" if reference else ""), file=out)

    reporter.RegisterUIHandler(show)
    return reporter

def errorCount(reporter):
    '''Return how many errors have been reported so far.'''

    return reporter.messageCounts[reporter.ERROR]

def messages(reporter):
    '''Return all messages except blank lines as plain dictionaries, for the run record.'''

    return [{"level": LEVELS[kind], "message": text, "ref": reference} for kind, text, reference in reporter.messages if kind != reporter.BLANK]
