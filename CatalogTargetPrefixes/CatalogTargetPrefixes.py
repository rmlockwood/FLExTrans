#
#   CatalogTargetPrefixes
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
#
#   Go through the database and extract the gloss field for each
#   prefix. Do this per sense. Write one gloss per line.
#

import sys
import re 
import os
import tempfile
import ReadConfig

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
import FTReport

from FTModuleClass import FlexToolsModuleClass

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Catalog Target Prefixes",
        'moduleVersion'    : 1,
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Creates a text file with glosses. REMEMBER to choose the target database before running!! ",
        'moduleDescription'   :
u"""
The target database set in the configuration file will be used. This module will output all 
the gloss fields for the best analysis writing system for morphtypes that are 'prefix.' 
NOTE: messages and the task bar will show the SOURCE database
as being used. Actually the target database is being used.
""" }


#----------------------------------------------------------------
# The main processing function
from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO import ITextRepository
from SIL.FieldWorks.FDO import IStText
from SIL.FieldWorks.FDO import IWfiGloss, IWfiWordform, IWfiAnalysis
from SIL.FieldWorks.FDO import ILexEntryRepository

from SIL.FieldWorks.FDO.DomainServices import SegmentServices

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError

from collections import defaultdict
from System import Guid
from System import String

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, 'TargetPrefixGlossListFile', report)
    if not outFileVal:
        return

    myPath = os.path.join(tempfile.gettempdir(), outFileVal)
    f_out = open(myPath, 'w') 

    TargetDB = FLExDBAccess()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            return
        TargetDB.OpenDatabase(targetProj, verbose = True)
    except FDA_DatabaseError, e:
        report.Error(e.message)
        print "FDO Cache Create failed!"
        print e.message
        return

    report.Info('Using: '+targetProj+' as the target database.')

    count = 0
    report.ProgressStart(TargetDB.LexiconNumberOfEntries())
  
    # Loop through all the entries
    for i,e in enumerate(TargetDB.LexiconAllEntries()):
    
        report.ProgressUpdate(i)
        
        # only process prefixes
        if e.LexemeFormOA and \
           e.LexemeFormOA.ClassName == 'MoAffixAllomorph' and \
           e.LexemeFormOA.MorphTypeRA and ITsString(e.LexemeFormOA.\
           MorphTypeRA.Name.BestAnalysisAlternative).Text in ('prefix'):
        
            # Set the headword value and the homograph #
            #headWord = re.sub(r' ', r'<b/>',ITsString(e.HeadWord).Text)
            
            # Loop through senses
            for i, mySense in enumerate(e.SensesOS):
                
                count += 1
                # Write out the gloss
                f_out.write(ITsString(mySense.Gloss.BestAnalysisAlternative).Text)
                f_out.write('\n')
                
    report.Info(str(count)+' prefixes exported to the catalog.')
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

