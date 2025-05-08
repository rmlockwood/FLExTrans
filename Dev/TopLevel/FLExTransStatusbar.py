#
#   Custom status bar callback for FLExTrans
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

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, QTranslator

app = QApplication(sys.argv)

# We need to set CURRENT_SRC_TEXT at the beginning so the statusbar can show the right thing.
configMap = ReadConfig.readConfig(None)

if configMap is None:
    FTPaths.CURRENT_SRC_TEXT = "ERROR: NO CONFIG FILE FOUND!!"
else:
    FTPaths.CURRENT_SRC_TEXT = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, None)

app.quit()
del app

def statusbarCallback():

    try:
        sourceText = FTPaths.CURRENT_SRC_TEXT 
    except AttributeError:
        sourceText = ""

    app = QApplication(sys.argv)

    # Define _translate for convenience
    _translate = QCoreApplication.translate

    # Load translations
    translator = QTranslator()

    if translator.load(FTPaths.TRANSL_DIR+f"/ReadConfig_{ReadConfig.getInterfaceLangCode()}.qm"):

        QCoreApplication.installTranslator(translator)

    # return a string that gets added to the status bar
    retStr = _translate("StatusBar","  Work Project: {project}    Source Text: {source_text}").format(project=FTPaths.WORK_PROJECT, source_text=sourceText)

    app.quit()
    del app

    return retStr