#
#   Custom status bar callback for FLExTrans
#
#   Version 3.14.1 - 9/6/25 - Ron Lockwood
#    Fixes #1064. Update status bar with whatever FTPaths.CURRENT_SRC_TEXT is set to every time.
#
#   Version 3.14 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.9 - 7/25/23 - Ron Lockwood
#    Bumped to 3.9
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function
#

import ReadConfig
import FTPaths 
import Utils

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication 

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'FLExTransStatusBar'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)


# We need to set CURRENT_SRC_TEXT at the beginning so the statusbar can show the right thing.
configMap = ReadConfig.readConfig(None)

if configMap is None:
    FTPaths.CURRENT_SRC_TEXT = "ERROR: NO CONFIG FILE FOUND!!"
else:
    FTPaths.CURRENT_SRC_TEXT = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, None)

# return a string that gets added to the status bar
retStr = _translate("FLExTransStatusbar","  Work Project: {project}    Source Text: ").format(project=FTPaths.WORK_PROJECT)

app.quit()
del app

def statusbarCallback():

    try:
        sourceText = FTPaths.CURRENT_SRC_TEXT 

    except AttributeError:

        sourceText = ""

    return retStr + sourceText