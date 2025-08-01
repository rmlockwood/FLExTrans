#
#   Guess_Semantic_Domains_Based_On_Gloss
#    - A FlexTools Module -
#
#   Attempt to match the gloss on senses to the example words 
#   given in the built-in Semantic Domains list.
#
#

from flextoolslib import *

from SIL.LCModel import ICmSemanticDomain

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Guess Semantic Domains (cast)",
        FTM_Version     : 2,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Add guessed Semantic Domains to senses based on glosses.",
        FTM_Description :
"""
Attempt to match the gloss on senses to the example words 
given in the built-in Semantic Domains list.
""" }
                 
#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    count = 0
    for sd in project.GetAllSemanticDomains(True):
        count      += 1
        report.Info("Semantic Domain: %s" % sd)
        report.Info(" ToString= %s" % sd.ToString())
        report.Info(" ClassName= %s" % sd.ClassName)
        report.Info(" type= %s" % type(sd))
        
        sd = ICmSemanticDomain(sd)   # Need to cast to the right type
        
        for question in sd.QuestionsOS:
            # question is a CmDomainQ
            report.Info("  Question: %s" % 
                        project.BestStr(question.Question))
            report.Info("     Example words: %s" %
                        project.BestStr(question.ExampleWords))
        break
        
    report.Info(f"Processed {count} semantic domains")

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
