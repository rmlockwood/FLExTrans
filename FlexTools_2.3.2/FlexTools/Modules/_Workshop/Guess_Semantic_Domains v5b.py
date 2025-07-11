#
#   Guess_Semantic_Domains_Based_On_Gloss
#    - A FlexTools Module -
#
#   Attempt to match the gloss on senses to the example words 
#   given in the built-in Semantic Domains list.
#
#

from flextoolslib import *

import re

from SIL.LCModel import ICmSemanticDomain, ILexSenseRepository

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Guess Semantic Domains (write)",
        FTM_Version     : "5b",
        FTM_ModifiesDB  : True,
        FTM_Synopsis    : "Add guessed Semantic Domains to senses based on glosses.",
        FTM_Description :
"""
Attempt to match the gloss on senses to the example words 
given in the built-in Semantic Domains list.
""" }
                 
#----------------------------------------------------------------

def tidyWord(word):
    word = word.strip(" ")          # spaces at start/end
    word = word.replace(" ", ".")   # change spaces to full-stops
    return word
    
def extractWords(wordlist):
    # Remove parentheticals first, as some have commas in them.
    wordlist = re.sub(r"\(.*?\)", "", wordlist) # parentheses
    words = wordlist.split(",")
    return [tidyWord(w) for w in words]



def Main(project, report, modifyAllowed):

    allWords = {}
    totalWordsFound = 0

    count = 0
    report.ProgressStart(1792)   # The number of SDs
    for sd in project.GetAllSemanticDomains(True):
        count      += 1
        report.ProgressUpdate(count)
        
        report.Info("Semantic Domain: %s" % sd)
        report.Info(f"{type(sd)}")
        sd = ICmSemanticDomain(sd)
        
        wordsInSD = 0
        for question in sd.QuestionsOS:
            # question is a CmDomainQ
            report.Info("  Question: %s" % 
                        project.BestStr(question.Question))
            wordlist = project.BestStr(question.ExampleWords)
            report.Info("     Example words: %s" % wordlist)
            
            words = extractWords(wordlist)
            
            for w in words:
                if w in allWords:
                    allWords[w].add(sd)
                else:
                    allWords[w] = set([sd])

            wordsInSD += len(words)
        
        report.Info(f"  {wordsInSD} words found.")
        totalWordsFound += wordsInSD
        
        if count > 5:
            break
            
    report.Info(f"Processed {count} semantic domains")
    report.Info(f"  {totalWordsFound} total words found; ({len(allWords)} unique words)")
    report.Info(f"  {allWords}")
    for w, sds in allWords.items():
        abbrevs = [project.BestStr(s.Abbreviation) for s in sds]
        report.Info(f"{w}: {', '.join(abbrevs)}")
        
    report.Blank()
    
    for sense in project.ObjectsIn(ILexSenseRepository):
       
        gloss = project.LexiconGetSenseGloss(sense)
        # report.Info(f"Gloss: {gloss}")
        
        if gloss in allWords:
            abbrevs = [project.BestStr(s.Abbreviation) for s in allWords[gloss]]
            report.Info(f"{gloss}: {abbrevs}",
                        project.BuildGotoURL(sense))
            if modifyAllowed:
                for sd in allWords[gloss]:
                    sense.SemanticDomainsRC.Add(sd)


#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
