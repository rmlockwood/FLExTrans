#
#   TextInOutUtils.py
#
#   Ron Lockwood
#   SIL International
#   7/1/24
#
#   Version 3.11 - 7/1/24 - Ron Lockwood
#    Initial version.
#
#   Shared functions, classes and constants for text in and out processing.
#

FT_SEARCH_REPLACE_ELEM = 'FLExTransSearchReplace' 
SEARCH_REPLACE_RULES_ELEM = 'SearchReplaceRules' 
SEARCH_REPL_RULE_ELEM = 'SearchReplaceRule' 
SEARCH_STRING_ELEM = 'SearchString'
REPL_STRING_ELEM = 'ReplaceString'
REGEX_ATTRIB = 'RegEx'
ARROW_CHAR = '⭢'

class SearchReplaceRuleData():

    def __init__(self, searchStr, replStr, isRegEx):

        self.searchStr = "" if searchStr is None else searchStr
        self.replStr = "" if replStr is None else replStr
        self.isRegEx = isRegEx

def getRuleFromElement(element):

    # Get the search and replace string elements
    searchEl = element[0]
    replaceEl = element[1]

    # Get the regex yes/no attribute
    regExVal = element.get(REGEX_ATTRIB)

    if regExVal == 'yes':
        isRegEx = True
    else:
        isRegEx = False

    searchReplaceRuleData = SearchReplaceRuleData(searchEl.text, replaceEl.text, isRegEx)

    return searchReplaceRuleData

def buildRuleString(searchStr, replStr, isRegExChecked):

    # Create a regex indicator string if reg ex is checked
    if isRegExChecked:

        regExStr = (' (✓ RegEx)')
    else:
        regExStr = ""

    # Build rule display string including codes for invisible chars.
    searchStr = getPrintableString(searchStr)
    replStr = getPrintableString(replStr)

    return f'{searchStr} {ARROW_CHAR} {replStr}{regExStr}'

def buildRuleStringFromElement(element):

    SRobj = getRuleFromElement(element)

    return buildRuleString(SRobj.searchStr, SRobj.replStr, SRobj.isRegEx)

def getPrintableString(myStr):
    
    # If we have a special char, return the equivalent alias str, otherwise return the char.
    return ''.join(replacementsMap.get(char, char) for char in myStr)

replacementsMap = {
'\u0000': '[NUL]','\u0001': '[SOH]','\u0002': '[STX]','\u0003': '[ETX]','\u0004': '[EOT]','\u0005': '[ENQ]','\u0006': '[ACK]','\u0007': '[BEL]','\u0008': '[BS]',
'\u0009': '[HT]', '\u0009': '[TAB]','\u000A': '[EOL]','\u000A': '[LF]', '\u000A': '[NL]', '\u000B': '[VT]', '\u000C': '[FF]', '\u000D': '[CR]', '\u000E': '[SO]','\u000F': '[SI]',
'\u0010': '[DLE]','\u0011': '[DC1]','\u0012': '[DC2]','\u0013': '[DC3]','\u0014': '[DC4]','\u0015': '[NAK]','\u0016': '[SYN]','\u0017': '[ETB]','\u0018': '[CAN]',
'\u0019': '[EM]', '\u0019': '[EOM]','\u001A': '[SUB]','\u001B': '[ESC]','\u001C': '[FS]', '\u001D': '[GS]', '\u001E': '[RS]', '\u001F': '[US]', '\u0020': '[SP]','\u007F': '[DEL]',
'\u0080': '[PAD]','\u0081': '[HOP]','\u0082': '[BPH]','\u0083': '[NBH]','\u0084': '[IND]','\u0085': '[NEL]','\u0086': '[SSA]','\u0087': '[ESA]','\u0088': '[HTS]',
'\u0089': '[HTJ]','\u008A': '[VTS]','\u008B': '[PLD]','\u008C': '[PLU]','\u008D': '[RI]', '\u008E': '[SS2]','\u008F': '[SS3]','\u0090': '[DCS]','\u0091': '[PU1]',
'\u0092': '[PU2]','\u0093': '[STS]','\u0094': '[CCH]','\u0095': '[MW]', '\u0096': '[SPA]','\u0097': '[EPA]','\u0098': '[SOS]','\u200B': '[ZWSP]','\u200C':'[ZWNJ]',
'\u200D': '[ZWJ]','\u200E': '[LRM]','\u200F': '[RLM]','\u202A': '[LRE]','\u202B': '[RLE]','\u202C': '[PDF]','\u202D': '[LRO]','\u202E': '[RLO]','\u202F': '[NNBSP]',
'\u205F': '[MMSP]','\u2060':'[WJ]', '\u2066': '[LRI]','\u2067': '[RLI]','\u2068': '[FSI]','\u2069': '[PDI]'
}
