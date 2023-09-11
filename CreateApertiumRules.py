#
#   CreateApertiumRules
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 3.9 - 9/11/23 - Ron Lockwood
#    Initial version
#
#   Given an xml file defining the rules, create Apertium-style rules

import Utils

import re
import os
import unicodedata

def CreateRules(DB, report, ruleAssistantFile, tranferRulePath):

    gramCategory= 'n'
    featureAbbrev = 'gender'
    
    # Use this function to get a list of tuples (lemma, featureValue) for this category that have this feature assigned. 
    # An empty list is returned if there are errors.
    lemmaList = Utils.getLemmasForFeature(DB, report, gramCategory, featureAbbrev)

    # Use this function to get a list of tuples (gloss, featureValue) for this category that have this feature assigned. 
    # An empty list is returned if there are errors.
    glossList = Utils.getAffixGlossesForFeature(DB, report, gramCategory, featureAbbrev)

    report.Info(f'lemma list: {", ".join(lemmaList[0])} ; {", ".join(lemmaList[1])}')

    report.Info(f'gloss list: {", ".join(glossList[0])} ; {", ".join(glossList[1])}')

    return True