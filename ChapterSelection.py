#
#   ChapterSelection
#
#   Ron Lockwood
#   SIL International
#   5/3/22
#
#   Version 3.7 - 1/25/23 - Ron Lockwood
#    Added cross-references to the selection class.
#
#   Version 3.5 - 5/3/22 - Ron Lockwood
#    Initial version.
#
#   ChapterSelection Class which is for data associated with import and export
#   from and to Paratext. 
#

bookMap = {\
'GEN':'Genesis',\
'EXO':'Exodus',\
'LEV':'Leviticus',\
'NUM':'Numbers',\
'DEU':'Deuteronomy',\
'JOS':'Joshua',\
'JDG':'Judges',\
'RUT':'Ruth',\
'1SA':'1 Samuel',\
'2SA':'2 Samuel',\
'1KI':'1 Kings',\
'2KI':'2 Kings',\
'1CH':'1 Chronicles',\
'2CH':'2 Chronicles',\
'EZR':'Ezra',\
'NEH':'Nehemiah',\
'EST':'Esther',\
'JOB':'Job',\
'PSA':'Psalms',\
'PRO':'Proverbs',\
'ECC':'Ecclesiastes',\
'SNG':'Song of Solomon',\
'ISA':'Isaiah',\
'JER':'Jeremiah',\
'LAM':'Lamentations',\
'EZK':'Ezekiel',\
'DAN':'Daniel',\
'HOS':'Hosea',\
'JOL':'Joel',\
'AMO':'Amos',\
'OBA':'Obadiah',\
'JON':'Jonah',\
'MIC':'Micah',\
'NAM':'Nahum',\
'HAB':'Habakkuk',\
'ZEP':'Zephaniah',\
'HAG':'Haggai',\
'ZEC':'Zechariah',\
'MAL':'Malachi',\
'MAT':'Matthew',\
'MRK':'Mark',\
'LUK':'Luke',\
'JHN':'John',\
'ACT':'Acts',\
'ROM':'Romans',\
'1CO':'1 Corinthians',\
'2CO':'2 Corinthians',\
'GAL':'Galatians',\
'EPH':'Ephesians',\
'PHP':'Philippians',\
'COL':'Colossians',\
'1TH':'1 Thessalonians',\
'2TH':'2 Thessalonians',\
'1TI':'1 Timothy',\
'2TI':'2 Timothy',\
'TIT':'Titus',\
'PHM':'Philemon',\
'HEB':'Hebrews',\
'JAS':'James',\
'1PE':'1 Peter',\
'2PE':'2 Peter',\
'1JN':'1 John',\
'2JN':'2 John',\
'3JN':'3 John',\
'JUD':'Jude',\
'REV':'Revelation',\
}

class ChapterSelection(object):
        
    def __init__(self, projectAbbrev, bookAbbrev, bookPath, fromChap, toChap, includeFootnotes, includeCrossRefs, makeActive, useFullBookName):
    
        self.projectAbbrev      = projectAbbrev    
        self.bookAbbrev         = bookAbbrev  
        self.bookPath           = bookPath     
        self.fromChap           = fromChap        
        self.toChap             = toChap          
        self.includeFootnotes   = includeFootnotes
        self.includeCrossRefs   = includeCrossRefs
        self.makeActive         = makeActive      
        self.useFullBookName    = useFullBookName     
        
    def dump(self):
        
        ret = {\
            'projectAbbrev'    : self.projectAbbrev      ,\
            'bookAbbrev'       : self.bookAbbrev         ,\
            'fromChap'         : self.fromChap           ,\
            'toChap'           : self.toChap             ,\
            'includeFootnotes' : self.includeFootnotes   ,\
            'includeCrossRefs' : self.includeCrossRefs   ,\
            'makeActive'       : self.makeActive         ,\
            'useFullBookName'  : self.useFullBookName     \
            }
        return ret
