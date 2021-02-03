#
#   CleanFiles
#
#   Remove key files to force each FLExTrans module to regenerate everything.
#
#

import os
from pathlib import Path
import tempfile
from FTModuleClass import *


#----------------------------------------------------------------
# Documentation that the user sees:
descr = "Clean files"
docs = {FTM_Name       : "Clean Files",
        FTM_Version    : '3.0',
        FTM_ModifiesDB : False,
        FTM_Synopsis   : descr,
        FTM_Help  : "",  
        FTM_Description:    descr}     
#----------------------------------------------------------------


OUTPUT = "Output\\"

# The main processing function
def MainFunction(DB, report, modify=True):
    
    try:
        os.remove(OUTPUT+'myText.syn')
    except:
        pass # ignore errors
    try:
        os.remove(OUTPUT+'myText.ana')
    except:
        pass # ignore errors
    try:
        os.remove(OUTPUT+'target_text.aper')
    except:
        pass # ignore errors
    try:
        os.remove(OUTPUT+'source_text.aper')
    except:
        pass # ignore errors
    try:
        os.remove(OUTPUT+'bilingual.dix')
    except:
        pass # ignore errors
    try:
        os.remove(OUTPUT+'target_pfx_glosses.txt')
    except:
        pass # ignore errors
    
    tempPath = tempfile.gettempdir()
    
    try:
        for p in Path(tempPath).glob("*_rt.dic"):
            p.unlink()
    except:
        pass # ignore errors
    
    try:
        for p in Path(tempPath).glob("*conversion_to_STAMP_cache.txt"):
            p.unlink()
    except:
        pass # ignore errors
    
    
    #remove root lexicon files in the tempfolder
    
    
    
        #report.Error("Deletion error, files might already be deleted.")

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
