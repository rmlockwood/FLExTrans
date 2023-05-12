#
#   A shell module to launch FlexTools
#
#   Version 3.8.1 - 5/12/23 - Ron Lockwood
#    Turn off dpi awareness.
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function
#

from flextoolslib import FTConfig, main

from Version import Title
from FLExTransMenu import customMenu

from FLExTransStatusbar import statusbarCallback

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(False)

   
main(Title, customMenu, statusbarCallback)
