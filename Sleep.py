#
#   Sleep
#
#   Sleep X seconds
#
#   Ron Lockwood
#   SIL International
#   1/20/15
#

from FTModuleClass import FlexToolsModuleClass
import time

#----------------------------------------------------------------
# Configurables:

sleepSeconds = 5

#----------------------------------------------------------------
# Documentation that the user sees:
descr = "Sleep for "+str(sleepSeconds)+" seconds."
docs = {'moduleName'       : "Sleep",
        'moduleVersion'    : '1.0',
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : descr,
        'moduleDescription': descr}
                 
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    for i in range(0,sleepSeconds):
        #report.Info(str(i)+" seconds of sleep remaining.")

        time.sleep(1)
 
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
