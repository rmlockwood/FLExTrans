#
#   fttranslator/__main__
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version.
#
#   OVERVIEW (AI generated, then edited)
#
#   Lets FTtranslator run as python -m fttranslator. The commands themselves are in cli.py; the exit code is the command's (0 for success).
#

import sys

from .cli import main

sys.exit(main())
