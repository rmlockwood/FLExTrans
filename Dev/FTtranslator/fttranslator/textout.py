#
#   fttranslator/textout
#
#   Ron Lockwood
#   SIL International
#   11/4/26
#
#   Version 3.17 - 11/4/26 - Ron Lockwood
#    Initial version. Applies a bundle's Text Out rules to the synthesized text without FieldWorks or Qt, as FLExTrans' Collect Output and Insert Target Text apply them.
#
#   OVERVIEW (AI generated, then edited)
#
#   The last step of an offline translation. On the desktop, the user's Text Out rules (the TextOutRulesFile setting, usually Output\fixup_synthesis_rules.xml) are a list of search and replace
#   rules applied to the synthesized text before it is shown or inserted: steps\finish.py calls TextInOutUtils.applyTextOutRulesFromConfig() for it. bundle.py copies the rules file into the
#   bundle as text_out_rules.xml, and this file applies it, so a project with rules gets the same translation offline as on the desktop.
#
#   WHY A PORT
#
#   TextInOutUtils.py can't be imported here: it is also the Text In/Out Rules editor, so it imports PyQt6, ReadConfig and Utils, and the Docker image holds only Dev\FTtranslator. The part that
#   applies rules has none of those needs, so it is copied below with the original names, so the two can be read side by side: getRuleFromElement(), buildRuleString() with
#   getPrintableString() and its replacementsMap (only for naming a failing rule), numRules(), create_replacer(), applyRulesToString() and applySearchReplaceRules(). The messages are the
#   desktop's English text, since the offline server has no Qt translator. tests/test_textout.py compares this port with TextInOutUtils.py whenever that can be imported.
#
#   THE RULES FILE
#
#   <FLExTransSearchReplace ApplyWildebeest="no"><SearchReplaceRules><SearchReplaceRule RegEx="no" Inactive="no" Comment="..."><SearchString/><ReplaceString/></SearchReplaceRule>...
#   The rules are applied in document order, each to the result of the one before. An inactive rule is skipped and isn't counted in the "rules applied" message. Wildebeest normalization is
#   switched off on the desktop (it doesn't run on Python 3.13), so ApplyWildebeest is ignored here too.
#
#   TRAPS
#
#    - Before each rule the text and the search string are put in NFD, as FieldWorks stores text, so a rule typed with composed characters still matches. The replacement is not normalized.
#    - Regular expression rules use the third-party regex module, not re, as the desktop does: the two differ (Unicode properties, possessive quantifiers), and a rule written against regex101
#      in FLExTrans has to behave the same here. The Dockerfile installs it.
#    - The replacement is interpreted by create_replacer(), not by regex.sub(), so \u, \l, \U, \L and \E work as in regex101, and \1 to \9 (and \0) are the only backreferences.
#    - A character class holding an accented letter quietly fails to match after NFD (the class gets the base letter and the mark as two members). The desktop editor warns about that; here it
#      just behaves the same way, which is the point.
#    - A failing rule stops all of them and the translation fails, as on the desktop, rather than showing the text half fixed up.
#
#   CODE STRUCTURE
#
#   SearchReplaceRuleData and the ported functions come first, in TextInOutUtils.py's order. TextOutRules holds one bundle's parsed rules file: load() reads it for a bundle (None when the bundle
#   has none), and apply() runs applySearchReplaceRules() and gives the (level, message) pairs offlineserver.py and cli.py's offline-stream show. RULES_FILE is the name bundle.py writes.
#

import os
import unicodedata
import xml.etree.ElementTree as ET

import regex

# The rules file's name in the bundle; bundle.py writes it and the manifest's files entry names it
RULES_FILE = "text_out_rules.xml"

# The module name the desktop's Collect Output gives applyTextOutRulesFromConfig() for its message
TEXT_OUT_MODULE_NAME = "Text Out"

SEARCH_REPLACE_RULES_ELEM = 'SearchReplaceRules'
REGEX_ATTRIB = 'RegEx'
INACTIVE_ATTRIB = 'Inactive'
COMMENT_ATTRIB = 'Comment'

ARROW_CHAR = '⭢'

class SearchReplaceRuleData():

    def __init__(self, searchStr, replStr, isRegEx, isInactive, comment):

        self.searchStr = "" if searchStr is None else searchStr
        self.replStr = "" if replStr is None else replStr
        self.isRegEx = isRegEx
        self.isInactive = isInactive
        self.comment = "" if comment is None else comment

def getRuleFromElement(element):
    '''One SearchReplaceRule element as a SearchReplaceRuleData: its search and replace strings are its first two children.'''

    searchEl = element[0]
    replaceEl = element[1]

    return SearchReplaceRuleData(searchEl.text, replaceEl.text, element.get(REGEX_ATTRIB) == 'yes', element.get(INACTIVE_ATTRIB) == 'yes', element.get(COMMENT_ATTRIB))

def buildRuleString(searchRplObj):
    '''A rule as the desktop shows it in its list and in the failure message: search ⭢ replace, then the RegEx, inactive and comment markers.'''

    regExStr = ' (✓ RegEx)' if searchRplObj.isRegEx else ""
    inactiveStr = '🚫' if searchRplObj.isInactive else ""
    commentStr = ' - ' + searchRplObj.comment if searchRplObj.comment else ''

    # Invisible characters are shown by their bracketed aliases
    searchStr = getPrintableString(searchRplObj.searchStr)
    replStr = getPrintableString(searchRplObj.replStr)

    return f'{searchStr} {ARROW_CHAR} {replStr}{regExStr}{inactiveStr}{commentStr}'

def getPrintableString(myStr: str):

    # If we have a special char, return the equivalent alias str, otherwise return the char.
    return ''.join(replacementsMap.get(char, char) for char in myStr)

# Copied from TextInOutUtils.py. Where a character is listed twice, as there, the later alias wins.
replacementsMap = {
'\u0000': '[NUL]','\u0001': '[SOH]','\u0002': '[STX]','\u0003': '[ETX]','\u0004': '[EOT]','\u0005': '[ENQ]','\u0006': '[ACK]','\u0007': '[BEL]','\u0008': '[BS]',
'\u0009': '[TAB]','\u000A': '[NL]', '\u000B': '[VT]', '\u000C': '[FF]', '\u000D': '[CR]', '\u000E': '[SO]','\u000F': '[SI]',
'\u0010': '[DLE]','\u0011': '[DC1]','\u0012': '[DC2]','\u0013': '[DC3]','\u0014': '[DC4]','\u0015': '[NAK]','\u0016': '[SYN]','\u0017': '[ETB]','\u0018': '[CAN]',
'\u0019': '[EOM]','\u001A': '[SUB]','\u001B': '[ESC]','\u001C': '[FS]', '\u001D': '[GS]', '\u001E': '[RS]', '\u001F': '[US]', ' ': '[SP]','\u007F': '[DEL]',
'\u0080': '[PAD]','\u0081': '[HOP]','\u0082': '[BPH]','\u0083': '[NBH]','\u0084': '[IND]','\u0085': '[NEL]','\u0086': '[SSA]','\u0087': '[ESA]','\u0088': '[HTS]',
'\u0089': '[HTJ]','\u008A': '[VTS]','\u008B': '[PLD]','\u008C': '[PLU]','\u008D': '[RI]', '\u008E': '[SS2]','\u008F': '[SS3]','\u0090': '[DCS]','\u0091': '[PU1]',
'\u0092': '[PU2]','\u0093': '[STS]','\u0094': '[CCH]','\u0095': '[MW]', '\u0096': '[SPA]','\u0097': '[EPA]','\u0098': '[SOS]','​': '[ZWSP]','‌':'[ZWNJ]',
'‍': '[ZWJ]','‎': '[LRM]','‏': '[RLM]','‪': '[LRE]','‫': '[RLE]','‬': '[PDF]','‭': '[LRO]','‮': '[RLO]',' ': '[NNBSP]',
' ': '[MMSP]','⁠':'[WJ]', '⁦': '[LRI]','⁧': '[RLI]','⁨': '[FSI]','⁩': '[PDI]'
}

def numRules(tree):
    '''The number of active rules, which the "rules applied" message gives.'''

    searchReplaceRulesElement = tree.getroot().find(SEARCH_REPLACE_RULES_ELEM)

    if searchReplaceRulesElement is not None:

        return sum(1 for ruleEl in searchReplaceRulesElement if not getRuleFromElement(ruleEl).isInactive)

    return 0

def create_replacer(pattern):
    r'''Return a replacement function for regex.sub() that reads the replacement pattern as regex101 does (Perl/PCRE semantics). See TextInOutUtils.create_replacer() for the full description:
       \0 to \9 insert a group, \u and \l change the case of the next character inserted, \U and \L that of everything up to \E (a \u or \l wins for its one character), and any other
       backslash sequence is passed through as typed.'''

    def replacer(match):

        result = ""
        i = 0

        # Case-forcing state: caseMode is set by \U or \L until \E or the end of the pattern; oneShotCase is set by \u or \l for the first character appended after it
        caseMode = None
        oneShotCase = None

        # Append text with the current case treatment: the pending \u or \l affects the first character and the enclosing \U or \L the rest
        def applyCase(text):

            nonlocal oneShotCase

            if not text:

                return ""

            firstChar = text[:1]
            restChars = text[1:]

            # A pending \u or \l wins over the enclosing \U or \L for this one character, then is used up
            if oneShotCase == 'upper':

                firstChar = firstChar.upper()
                oneShotCase = None

            elif oneShotCase == 'lower':

                firstChar = firstChar.lower()
                oneShotCase = None

            elif caseMode == 'upper':

                firstChar = firstChar.upper()

            elif caseMode == 'lower':

                firstChar = firstChar.lower()

            # The remaining characters get only the enclosing \U or \L
            if caseMode == 'upper':

                restChars = restChars.upper()

            elif caseMode == 'lower':

                restChars = restChars.lower()

            return firstChar + restChars

        while i < len(pattern):

            if pattern[i] == '\\' and i + 1 < len(pattern):

                nextChar = pattern[i+1]

                # Backreferences \0 - \9, with the current case treatment
                if nextChar.isdigit():

                    result += applyCase(match.group(int(nextChar)) or "")
                    i += 2

                # \u and \l only record what to do; applyCase() does it to whatever is inserted next
                elif nextChar == 'u' or nextChar == 'l':

                    oneShotCase = 'upper' if nextChar == 'u' else 'lower'
                    i += 2

                # \U and \L start case forcing that lasts until \E or the end of the pattern
                elif nextChar == 'U' or nextChar == 'L':

                    caseMode = 'upper' if nextChar == 'U' else 'lower'
                    i += 2

                elif nextChar == 'E':

                    caseMode = None
                    i += 2

                # Any other backslash sequence is passed through; the backslash goes in raw so a pending \u or \l isn't used up on it
                else:
                    result += pattern[i]
                    i += 1

            # An ordinary literal character
            else:
                result += applyCase(pattern[i])
                i += 1

        return result

    return replacer

def applyRulesToString(inputStr, numberedRules):
    '''Apply (ruleNumber, ruleEl) pairs in order, skipping inactive rules. Returns (newStr, errorMsg): on a failure newStr is the text as the rules before it left it and errorMsg names the
       rule; otherwise errorMsg is "".'''

    errorMsg = ""
    newStr = inputStr

    for ruleNumber, ruleEl in numberedRules:

        searchReplObj = getRuleFromElement(ruleEl)

        if searchReplObj.isInactive:

            continue

        # FLEx stores text decomposed, but the user may not have typed the rule decomposed. See TRAPS above.
        newStr = unicodedata.normalize('NFD', newStr)
        newSearch = unicodedata.normalize('NFD', searchReplObj.searchStr)

        # The desktop catches everything here (a bare except); a bad regular expression is the usual cause
        try:
            if searchReplObj.isRegEx:

                newStr = regex.sub(newSearch, create_replacer(searchReplObj.replStr), newStr)

            else:
                newStr = newStr.replace(newSearch, searchReplObj.replStr)

        except Exception:

            errorMsg = f"Applying Text In/Out rules stopped because of a failure of rule {ruleNumber}: {buildRuleString(searchReplObj)}"
            break

    return newStr, errorMsg

def applySearchReplaceRules(inputStr, tree):
    '''Apply every rule in the tree, numbered from 1. Returns (newStr, errorMsg), with newStr None on a failure, as the desktop's callers expect.'''

    searchReplaceRulesElement = tree.getroot().find(SEARCH_REPLACE_RULES_ELEM)

    # The desktop would fail on a file with no rules element; here it simply has no rules
    if searchReplaceRulesElement is None:

        return inputStr, ""

    numberedRules = [(ruleNumber + 1, ruleEl) for ruleNumber, ruleEl in enumerate(searchReplaceRulesElement)]
    newStr, errorMsg = applyRulesToString(inputStr, numberedRules)

    if errorMsg:

        return None, errorMsg

    return newStr, errorMsg

class TextOutRules:
    '''One bundle's Text Out rules, parsed once. See the OVERVIEW above.'''

    def __init__(self, tree):

        self.tree = tree

    @classmethod
    def load(cls, bundleDir, manifest):
        '''The bundle's rules, or None when it has none (a bundle made before rules were exported has no textOutRules entry). A rules file with bad XML raises ET.ParseError, though
           bundle.py refuses to export one.'''

        fileName = manifest.get("files", {}).get("textOutRules")

        if not fileName:

            return None

        path = os.path.join(bundleDir, fileName)

        if not os.path.exists(path):

            return None

        return cls(ET.parse(path))

    def apply(self, text):
        '''Apply the rules to the synthesized text. Returns (newText, messages): newText is None when a rule failed, and messages holds the desktop's info or error as a (level, text) pair.'''

        newText, errorMsg = applySearchReplaceRules(text, self.tree)

        if newText is None:

            return None, [("error", errorMsg)]

        return newText, [("info", f"{numRules(self.tree)} {TEXT_OUT_MODULE_NAME} rules applied.")]
