#
#   Utils
#
#   Ron Lockwood
#   SIL International
#   7/23/2014
#
#   Shared functions

import re

# Append '1' to the headWord if there is no homograph #
def add_one(headWord): 
    if not re.search('(\d$)', headWord):
        return (headWord + '1')
    else:
        return headWord 

# Duplicate the capitalization of the model word on the input word
def do_capitalization(wordToChange, modelWord):
    if wordToChange and modelWord:
        if modelWord.isupper():
            return wordToChange.upper()
        elif modelWord[0].isupper():
            return wordToChange[0].upper()+wordToChange[1:]
        else:
            return wordToChange
