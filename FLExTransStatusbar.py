#
#   Custom status bar callback for FLExTrans
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function
#

import ReadConfig
import FTPaths 

# We need to set CURRENT_SRC_TEXT at the beginning so the statusbar can show the right thing.
configMap = ReadConfig.readConfig(None)
FTPaths.CURRENT_SRC_TEXT = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, None)

def statusbarCallback():
    try:
        sourceText = FTPaths.CURRENT_SRC_TEXT 
    except AttributeError:
        sourceText = ""

    # return a string that gets added to the status bar
    return(f"  Work Project: {FTPaths.WORK_PROJECT}    Source Text: {sourceText}")
  
 