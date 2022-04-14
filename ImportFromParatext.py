#
#   ImportFromParatext
#
#   Ron Lockwood
#   SIL International
#   10/30/21
#
#   Version 3.1 - 2/4/22 - Ron Lockwood
#    Initial version.
#
#   Import chapters from Paratext. The user is prompted which chapters and which
#   Paratext project.
#
#

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from SIL.LCModel.Core.Text import TsStringUtils
from flexlibs.FLExProject import FLExProject, GetProjectNames
import ReadConfig
import os
import re
import glob

#----------------------------------------------------------------
# Configurables:
PTXPATH = 'C:\\My Paratext 8 Projects'
PTXPROJABBREV = 'AMIU'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Import Text From Paratext",
        FTM_Version    : "3.2",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Import chapters from Paratext.",
        FTM_Help       : "",
        FTM_Description:
"""
Copy chapters of a given book from a given Paratext project import it into the source FLEx project.
The copied chapters will show up as a new text in the FLEx project. If the text already exists, a
new text will get created with a similar name. You have to have at least an Observer role on the 
project.""" }
                 
#----------------------------------------------------------------
# The main processing function

textNameList = []

def MainFunction(DB, report, modify=True):
    
    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not (sourceTextName):
        return
    
    if re.search(' ', sourceTextName) == None:
        report.Error('Source name must be in the format: [BookName|BookAbbr] Ch(:verse-verse)')
        return
        
    ## Find the text we want from Paratext

    # Get [BookName|BookAbbr], chapter, and beg/end verses
    parts = sourceTextName.split(':')
    
    if len(parts) < 2: # no verses
        
        begVrs = 0
        endVrs = 999
    else:
        if re.search('-', sourceTextName) == None:
            report.Error('Source name must be in the format: [BookName|BookAbbr] Ch(:verse-verse)')
            return
        
        begVrs, endVrs = parts[1].split('-')
        begVrs = int(begVrs)
        endVrs = int(endVrs)
    
    bookAbbrev, chNum = parts[0].split(' ')
    
    if chNum.isdigit() == False or int(chNum) == 0 or int(chNum) > 150:
        report.Error('Invalid chapter number.')
        report.Error('Source name must be in the format: [BookName|BookAbbr] Ch(:verse-verse)')
        return
    
    chNum = int(chNum)
    
    ## Do some error checking on the text name
    
    if len(bookAbbrev) == 3:
        
        bookAbbrev = bookAbbrev.upper()
        
    # Check for valid book abbreviation
    if bookAbbrev not in bookMap.values():
    
        # Accept full book name instead of abbrev.
        if bookAbbrev in bookMap:
            
            bookAbbrev = bookMap[bookAbbrev]
        else:
            report.Error('Invalid Bible book name: ' + bookAbbrev)
            return
            
    # Open the Paratext file, use a wildcard in place of number
    filename = os.path.join(PTXPATH, PTXPROJABBREV, '*' + bookAbbrev + PTXPROJABBREV + '.SFM')
    
    parts = glob.glob(filename)
    if len(parts) < 1:
        report.Error('File not found: ' + filename)
        return

    filename = parts[0]
    
    # Open the file
    f = open(filename, encoding='utf-8')
    
    # Create the text objects
    m_textFactory = DB.project.ServiceLocator.GetInstance(ITextFactory)
    m_stTextFactory = DB.project.ServiceLocator.GetInstance(IStTextFactory)
    m_stTxtParaFactory = DB.project.ServiceLocator.GetInstance(IStTxtParaFactory)

    # Create a text and add it to the project      
    text = m_textFactory.Create()           
    stText = m_stTextFactory.Create()
    
    # Set StText object as the Text contents
    text.ContentsOA = stText  
    
    haveChap = False
    chunk = ''
    
    # Get the lines for the desired chapter
    for line in f:
        
        if haveChap and re.search(r'\\c', line):
            
            haveChap = False
            
        if re.search(r'\\c ' + str(chNum) + r'$', line):
            
            haveChap = True
            
        if haveChap:
            
            chunk += line
            
    f.close()
    
    # remove newlines?
    
    ## Now get only the verses desired
    
    # split at verse #s
    versSegs = re.split(r'(\\v \d+)', chunk)
          
    savedTxt = ''
      
    if begVrs <= 1:
        savedTxt += versSegs[0]
    
    for i, seg in enumerate(versSegs):
        
        if re.search(r'\\v', seg):
        
            verse = int(seg.split()[1])
            
            if verse >= begVrs and verse <= endVrs:
                
                savedTxt += seg + versSegs[i+1]
        
    # Replace new line with space if it's before a marker
    outStr = re.sub(r'\n\\', r' \\', savedTxt)
    
    segs = re.split(r'(\\f\*|\\f \+ |\\fr \d+:\d+|\\v \d+ |\\c \d+|\\\w+ )', outStr) # match either \v n or \c n or other sfms

    # Create 1st paragraph object
    stTxtPara = m_stTxtParaFactory.Create()
    
    # Add it to the stText object
    stText.ParagraphsOS.Add(stTxtPara)    

    bldr = TsStringUtils.MakeStrBldr()

    for i, seg in enumerate(segs):
        
        if re.search(r'\\p', seg): # or first segment if not blank
        
            # Save the built up string to the Contents member
            stTxtPara.Contents = bldr.GetString()
            
            # Create paragraph object
            stTxtPara = m_stTxtParaFactory.Create()
            
            # Add it to the stText object
            stText.ParagraphsOS.Add(stTxtPara)  
        
            bldr = TsStringUtils.MakeStrBldr()
        
        # Remove newlines
        seg = re.sub(r'\n', '', seg)
        
        if len(seg) == 0:
            continue
        
        elif re.search(r'\\', seg):
            
            # make this in the Analysis WS
            tss = TsStringUtils.MakeString(seg, DB.project.DefaultAnalWs)
            bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
            
        else:
            # make this in the Vernacular WS
            tss = TsStringUtils.MakeString(seg, DB.project.DefaultVernWs)
            bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
        
    stTxtPara.Contents = bldr.GetString()

    # Set the title of the text
    tss = TsStringUtils.MakeString(sourceTextName, DB.project.DefaultAnalWs)
    text.Name.AnalysisDefaultWritingSystem = tss
    
    report.Info('Text: "'+sourceTextName+'" created.')

bookMap = {\
'Genesis':'GEN',\
'Exodus':'EXO',\
'Leviticus':'LEV',\
'Numbers':'NUM',\
'Deuteronomy':'DEU',\
'Joshua':'JOS',\
'Judges':'JDG',\
'Ruth':'RUT',\
'1 Samuel':'1SA',\
'2 Samuel':'2SA',\
'1 Kings':'1KI',\
'2 Kings':'2KI',\
'1 Chronicles':'1CH',\
'2 Chronicles':'2CH',\
'Ezra':'EZR',\
'Nehemiah':'NEH',\
'Esther':'EST',\
'Job':'JOB',\
'Psalms':'PSA',\
'Proverbs':'PRO',\
'Ecclesiastes':'ECC',\
'Song of Solomon':'SNG',\
'Isaiah':'ISA',\
'Jeremiah':'JER',\
'Lamentations':'LAM',\
'Ezekiel':'EZK',\
'Daniel':'DAN',\
'Hosea':'HOS',\
'Joel':'JOL',\
'Amos':'AMO',\
'Obadiah':'OBA',\
'Jonah':'JON',\
'Micah':'MIC',\
'Nahum':'NAM',\
'Habakkuk':'HAB',\
'Zephaniah':'ZEP',\
'Haggai':'HAG',\
'Zechariah':'ZEC',\
'Malachi':'MAL',\
'Matthew':'MAT',\
'Mark':'MRK',\
'Luke':'LUK',\
'John':'JHN',\
'Acts':'ACT',\
'Romans':'ROM',\
'1 Corinthians':'1CO',\
'2 Corinthians':'2CO',\
'Galatians':'GAL',\
'Ephesians':'EPH',\
'Philippians':'PHP',\
'Colossians':'COL',\
'1 Thessalonians':'1TH',\
'2 Thessalonians':'2TH',\
'1 Timothy':'1TI',\
'2 Timothy':'2TI',\
'Titus':'TIT',\
'Philemon':'PHM',\
'Hebrews':'HEB',\
'James':'JAS',\
'1 Peter':'1PE',\
'2 Peter':'2PE',\
'1 John':'1JN',\
'2 John':'2JN',\
'3 John':'3JN',\
'Jude':'JUD',\
'Revelation':'REV',\
}

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
