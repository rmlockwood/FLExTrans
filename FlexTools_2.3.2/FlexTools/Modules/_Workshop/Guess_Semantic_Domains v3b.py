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

from SIL.LCModel import ICmSemanticDomain

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Guess Semantic Domains (parse words B)",
        FTM_Version     : "3b",
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Add guessed Semantic Domains to senses based on glosses.",
        FTM_Description :
"""
Attempt to match the gloss on senses to the example words 
given in the built-in Semantic Domains list.
""" }
                 
#----------------------------------------------------------------

def tidyWord(word):
    word = re.sub(r"\(.*?\)", "", word) # parentheses
    word = word.strip(" ")              # spaces at start/end
    word = word.replace(" ", ".")       # change spaces to full-stops
    return word
    
def extractWords(wordlist):
    words = wordlist.split(",")
    return [tidyWord(w) for w in words]



def Main(project, report, modifyAllowed):

    allWords = set()
    totalWordsFound = 0

    count = 0
    for sd in project.GetAllSemanticDomains(True):
        count      += 1
        report.Info("Semantic Domain: %s" % sd)
        sd = ICmSemanticDomain(sd)
        
        wordsInSD = 0
        for question in sd.QuestionsOS:
            # question is a CmDomainQ
            report.Info("  Question: %s" % 
                        project.BestStr(question.Question))
            wordlist = project.BestStr(question.ExampleWords)
            report.Info("     Example words: %s" % wordlist)
            
            words = extractWords(wordlist)
            allWords.update(set(words))

            wordsInSD += len(words)
        
        report.Info(f"  {wordsInSD} words found.")
        totalWordsFound += wordsInSD
        
        if count > 5:
            break
            
    report.Info(f"Processed {count} semantic domains")
    report.Info(f"  {totalWordsFound} total words found; ({len(allWords)} unique words)")
    report.Info(f"  {allWords}")

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
