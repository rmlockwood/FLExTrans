#
#   CompareTestBedResults
#
#   Ron Lockwood
#   SIL International
#   2/11/16
#
#   Launch FLExApps at the given path.
#

from __future__ import unicode_literals

from FTModuleClass import *

import re
from types import *
import os
import shutil
import difflib
import unicodedata

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Compare Testbed Results",
        FTM_Version    : "1.0",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Compare results to the gold standard",
        FTM_Help       : None,
        FTM_Description:
"""
Compare results to the gold standard.
""" }

#----------------------------------------------------------------
# The main processing function

def write_results(currentTestRun, proj_map, xmlLogFile, report):
    
    # Save a copy of our xml file
    shutil.copy2(xmlLogFile, xmlLogFile+'.old')

    # Open log file
    f = open(xmlLogFile)
    myLines = []
    for l in f:
        l = unicode(l,'utf-8')
        myLines.append(l)
    f.close()
    
    f = open(xmlLogFile, "w")
    
    j = open('junk2.txt','w')
    # Write results
    for line in myLines:
        f.write(line.encode('utf-8'))
        
        if re.search('<test n="'+currentTestRun+'">', line):
            
            # write the new data here
            # loop through all the projects
            for proj_name, gold_map in sorted(proj_map.items(), key=lambda x: x[0]):
                
                # output project name
                f.write('    <project n="'+proj_name+'">\n')

                # loop through all the files with associated diff data
                for gold_file, results in sorted(gold_map.items(), key=lambda x: x[0]):

                    # output file name
                    f.write('      <file n="'+gold_file+'">\n')
                    f.write('        <diffs>\n')
                    f.write('          <![CDATA[\n')

                    # output all the result lines
                    for diff_line in results:
                        
                        f.write(diff_line.strip().encode('utf-8')+'\n'.encode('utf-8')) # should already have a newline present

                    f.write('          ]]>\n')
                    f.write('        </diffs>\n')
                    f.write('      </file>\n')

                f.write('    </project>\n')
                
    return
    
TempFiles = ['myText.ana','myText.syn']   
#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    testbedRootFolder = 'C:\\Data\\FLExTrans\\Testbed\\'
    goldStandardFolder =  testbedRootFolder+'GoldStandard'
    ResultsFolder =  testbedRootFolder+'Results'

    # Get the parent (date/time) folder
    # Read a string out of a file that keeps the current name of the test run
    f = open(testbedRootFolder+'Results\\CurrentTestRunName.txt') 
    currentTestRun = f.read()
    
    # Get log file name
    xmlLogFile = testbedRootFolder+'Results\\TestbedLog.xml'
    
    # Read all the test project folder names
    projNames = os.listdir(goldStandardFolder)
    proj_map = {}
    
    diff_count = 0
    
    # Loop through all the projects
    for projName in projNames:
        
        gold_map = {}
        # Get list of gold standard files
        goldFiles = os.listdir(goldStandardFolder+'\\'+projName)
        
        # Loop through all gold files
        for goldFile in sorted(goldFiles):
            
            # Compare the files
            g = open(goldStandardFolder+'\\'+projName+'\\'+goldFile)
            r = open(ResultsFolder+'\\'+currentTestRun+'\\'+projName+'\\'+goldFile)
            gList = []
            for l in g:
                l = unicode(l,'utf-8')
                gList.append(l)
                
            rList = []
            for l in r:
                l = unicode(l,'utf-8')
                rList.append(l)
                
            # If different
            if gList != rList:
                
                diff_count += 1
                
                # if source, target (*.aper) or synthesized (*.syn) text do a detailed diff
                if re.search(r'\.(aper|syn)$', goldFile):
                    
                    d = difflib.Differ()
                    result = list(d.compare(gList, rList))
                    
                else: # do a unified diff
                    
                    result = difflib.unified_diff(gList, rList, fromfile=g, tofile=r)
                    
#                     j = open('junk.txt', 'w')
#                     for r in result:
#                         j.write(r.encode('utf-8'))
#                         
#                     return
        
                gold_map[goldFile] = result
        proj_map[projName] = gold_map
    write_results(currentTestRun, proj_map, xmlLogFile, report)
    
    if diff_count == 0:
        report.Info('No differences found!')
    else: 
        report.Info('Differences found in '+str(diff_count)+' files.')
    
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
