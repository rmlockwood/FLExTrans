#
#   syncTransferCss.py
#
#   Build tool. Propagates structural changes in the master XXE rule-preview stylesheet
#     Installer/InstallerResources/XXEaddon/ApertiumTransferXMLmind/css/transfer.css
#   into each translation-language copy under
#     Installer/InstallerResources/XXEaddon/translations/<code>/ApertiumTransferXMLmind/css/transfer.css
#
#   The translated copies are structurally identical to the master (same selectors, fields, colours, layout) and differ ONLY in the quoted label strings inside `content:` declarations
#   (e.g. " action: " -> " Aktion: "). This tool rebuilds each translated copy FROM the master so every non-string change (a new element rule, a colour edit, a renamed/added field) is
#   carried over automatically, while re-applying the translations that copy already had. Any English string in the master that the translated copy has no translation for is left in
#   English and reported, so the translator knows exactly what to translate next.
#
#   Run it after editing the master transfer.css (CreateInstaller.bat runs it just before derive_preview_specs.py so a build never ships mismatched copies):
#     python Dev/syncTransferCss.py
#
#   See Dev/README-AddingUILanguage.md for the whole preview-stylesheet story.
#
#   Notes / limits: comments and everything outside quoted content strings come from the master verbatim, so a translated copy's comments are reset to the master's English. Translations
#   are matched to master strings by (selector, which-occurrence-of-that-selector, position-of-the-string-within-that-rule); reordering strings inside one rule can therefore un-match them
#   (they'd be reported as needing translation). Each translated file is rewritten in the encoding it is currently stored in (the existing copies are cp1252), so its own characters round-trip.

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XXE = os.path.join(REPO, 'Installer', 'InstallerResources', 'XXEaddon')

# The UI-language list comes from the single authoritative module in Dev/Lib.
sys.path.insert(0, os.path.join(REPO, 'Dev', 'Lib'))
import UILanguages

MASTER_CSS = os.path.join(XXE, 'ApertiumTransferXMLmind', 'css', 'transfer.css')

# A CSS rule block: the run of text up to '{' (the selector, plus any comment/whitespace before it) and the body between the braces. The stylesheet is flat (no nested blocks), same
# assumption derive_preview_specs.py makes.
RULE_RE = re.compile(r'([^{}]+)\{([^{}]*)\}', re.DOTALL)


def transCssPath(code):
    '''The translated stylesheet path for a language code.'''

    return os.path.join(XXE, 'translations', code, 'ApertiumTransferXMLmind', 'css', 'transfer.css')


def decodeBytes(data):
    '''Decode a stylesheet's bytes, returning (text, encoding). The translated copies are cp1252, not UTF-8; try UTF-8 first (covers the ASCII master and any UTF-8 file) and fall back to
    cp1252 so accented labels survive. The encoding is returned so the file can be written back in the same one.'''

    for enc in ('utf-8', 'cp1252'):

        try:
            return data.decode(enc), enc

        except UnicodeDecodeError:
            continue

    return data.decode('cp1252', errors='replace'), 'cp1252'


def findStrings(body):
    '''Return the (start, end, text) spans of the double-quoted strings in a rule body, skipping any inside /* ... */ comments. These quoted strings are the translatable label text
    (the leading `content:` label plus any check-box/combo-box labels); everything else in the body is structure.'''

    spans = []
    i, n = 0, len(body)

    while i < n:

        if body[i:i + 2] == '/*':

            end = body.find('*/', i + 2)
            i = n if end == -1 else end + 2
            continue

        if body[i] == '"':

            end = body.find('"', i + 1)

            if end == -1:
                break

            spans.append((i, end + 1, body[i + 1:end]))
            i = end + 1
            continue

        i += 1

    return spans


def buildCatalog(text):
    '''Build a {(selector, occurrence, stringIndex): translatedString} map from a translated stylesheet, so a master string at the same position can be looked up. Keying by selector (not
    by absolute position in the file) keeps existing translations matched even when the master has gained or lost whole rules elsewhere.'''

    catalog = {}
    selectorOccurrences = {}

    for match in RULE_RE.finditer(text):

        selector = match.group(1).strip()
        occurrence = selectorOccurrences.get(selector, 0)
        selectorOccurrences[selector] = occurrence + 1

        for stringIndex, (start, end, stringText) in enumerate(findStrings(match.group(2))):
            catalog[(selector, occurrence, stringIndex)] = stringText

    return catalog


def regenerate(masterText, catalog):
    '''Rebuild a translated stylesheet from the master text, replacing each quoted label string with its translation from `catalog`. Returns (newText, missing) where `missing` lists the
    (selector, englishString) pairs the catalog had no translation for (left in English in the output).'''

    selectorOccurrences = {}
    missing = []

    def replaceRule(match):

        selectorRaw, body = match.group(1), match.group(2)
        selector = selectorRaw.strip()
        occurrence = selectorOccurrences.get(selector, 0)
        selectorOccurrences[selector] = occurrence + 1

        # Replace the strings right-to-left so earlier spans' offsets stay valid as we splice.
        spans = findStrings(body)
        newBody = body

        for stringIndex in range(len(spans) - 1, -1, -1):

            start, end, english = spans[stringIndex]
            translated = catalog.get((selector, occurrence, stringIndex))

            if translated is None:

                translated = english

                if english.strip():
                    missing.append((selector, english))

            newBody = newBody[:start] + '"' + translated + '"' + newBody[end:]

        return selectorRaw + '{' + newBody + '}'

    return RULE_RE.sub(replaceRule, masterText), missing


def main():

    print('Syncing translated transfer.css copies from the master ({master}):'.format(master=os.path.relpath(MASTER_CSS, REPO)))

    masterText, _ = decodeBytes(open(MASTER_CSS, 'rb').read())

    for code in UILanguages.translationCodes():

        path = transCssPath(code)

        if not os.path.isfile(path):

            print('  SKIP {code}: {path} not found (create it per step 4 of README-AddingUILanguage.md)'.format(code=code, path=os.path.relpath(path, REPO)))
            continue

        oldText, encoding = decodeBytes(open(path, 'rb').read())
        catalog = buildCatalog(oldText)
        newText, missing = regenerate(masterText, catalog)

        # De-duplicate the needs-translation list, preserving first-seen order, so a string used in several rules is reported once.
        missingSeen = []

        for selector, english in missing:

            if english not in missingSeen:
                missingSeen.append(english)

        if newText == oldText:

            print('  {code}: unchanged'.format(code=code))

        else:

            open(path, 'wb').write(newText.encode(encoding))
            print('  {code}: updated ({path}, {enc})'.format(code=code, path=os.path.relpath(path, REPO), enc=encoding))

        if missingSeen:

            print('    {n} string(s) still in English (need translation in {code}):'.format(n=len(missingSeen), code=code))

            for english in missingSeen:
                print('      "{english}"'.format(english=english))


if __name__ == '__main__':
    main()
