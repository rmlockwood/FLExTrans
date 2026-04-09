#
#   A shell module to launch FlexTools
#
#   Version 3.15.2 - 4/8/26 - Ron Lockwood
#    Fix scaling issues. #65 in FlexTools GitHub repo.
#    Move SetProcessDpiAwareness to the top of the file to ensure 
#    it takes effect before any GUI elements are created.
#
#   Version 3.15.1 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.9 - 7/25/23 - Ron Lockwood
#    Bumped to 3.9
#
#   Version 3.8.1 - 5/12/23 - Ron Lockwood
#    Turn off dpi awareness.
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function
#

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(0)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

from flextoolslib import FTConfig, main

from Version import Title
from FLExTransMenu import customMenu

from FLExTransStatusbar import statusbarCallback
   
main(Title, customMenu, statusbarCallback)
