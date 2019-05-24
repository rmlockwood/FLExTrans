#
#   ExtractFree.py
#
#   Ron Lockwood
#   SIL International
#   
#   Check to see if the citation form is the same as the lexeme form.

import re

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   

from __DuplicatesConfig import *

from collections import defaultdict
from types import *


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Export Free Translations",
        FTM_Version    : "1.0",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Export Free Translations.",
        FTM_Help       : "",
        FTM_Description:
u"""
Export Free Translations.
""" }


#----------------------------------------------------------------

def MainFunction(DB, report, modifyAllowed):

    wsSet = DB.GetAllAnalysisWSs()
    
    #wsSet.remove('fi')
    #wsSet.remove('mvp')
    
    for text in DB.ObjectsIn(ITextRepository):
        # open text file
        text_name = ITsString(text.Name.BestAnalysisAlternative).Text
        
        text_name = re.sub('[\\/:\*\?\"<>\|]','-', text_name)
        f = open(text_name+'.txt','w')
        
        if text.ContentsOA:
            # get contents object
            contents = text.ContentsOA

            if contents.ParagraphsOS:
                # loop through each paragraph
                for para in contents.ParagraphsOS:
                    
                    outBaseline = ''
                    
                    outFreeList = []
                    
                    for i, x in enumerate(wsSet):
                        outFreeList.append(unicode('')) 
                    
                    if para.SegmentsOS:
                        # loop through each segment
                        for j, seg in enumerate(para.SegmentsOS):
                            
                            # get begin and end offsets
                            beg = seg.BeginOffset
                            
                            # find end offset
                            next_seg_index = j + 1
                            
                            # it's either the beginning of the next segment 
                            seg_count = para.SegmentsOS.Count
                            if next_seg_index < seg_count:
                                end = para.SegmentsOS.ToArray()[next_seg_index].BeginOffset 
                                
                            # or if there's no next segment, the end of the paragraph
                            else:
                                end = len(ITsString(para.Contents).Text)
                            
                            # get baseline text
                            baseStr =  ITsString(para.Contents).Text[beg:end]
            
                            outBaseline += baseStr
                            
                            # get free translations
                            for  i, ws in enumerate(wsSet):
                                
                                if seg.FreeTranslation:
                                    hvo = DB.WSHandle(ws)
                                    multiString = seg.FreeTranslation.get_String(hvo)
                                    myStr =  ITsString(multiString).Text
                                    
                                    if myStr:
                                        outFreeList[i] += myStr
                    
                        # write out the data
                        f.write(outBaseline.encode('utf-8') + '\n')
                        
                        for outStr in outFreeList:
                            f.write(outStr.encode('utf-8') + '\n')
                            
                        f.write('\n')
                
        f.close()



                
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
