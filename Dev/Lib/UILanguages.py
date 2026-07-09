#
#   UILanguages
#
#   Ron Lockwood
#   SIL International
#   7/9/26
#
#   Version 3.16 - 7/9/26 - Ron Lockwood
#    Initial version. The single authoritative list of the user-interface languages FLExTrans supports.
#
#   THE single authoritative definition of the FLExTrans user-interface languages. See README-AddingUILanguage.md
#
#   TO ADD A UI LANGUAGE: add one UILang line to LANGUAGES below, then do the rest of the steps in README-AddingUILanguage.md
#
#   This module is deliberately Qt-free so build tools can import it without PyQt installed.

from collections import namedtuple

# One record per UI language:
#   code        - the two-letter code used everywhere in FLExTrans: .qm/.ts suffixes, preview_spec_<code>.json, flextools.ini uilanguage, XXE addon zip names, etc.
#   englishName - the language's name in English (shown e.g. as the default explanation language in Work on Rules with AI).
#   nativeName  - the language's name in itself (what the installer's language picker shows; must match XX_DISPLAY_NAME in LangForInstallerScript/XX.nsh).
#   localeName  - the locale used for date/time formatting (passed to QLocale()).
#   nsisName    - the NSIS language-file name: MUI_LANGUAGE "<nsisName>" registers it, and ${LANG_<NSISNAME uppercased>} is its language-id constant.
#   crowdinId   - the Crowdin language id, only when it differs from the two-letter code (Crowdin calls Spanish 'es-ES'); None means the code is used as is.
UILang = namedtuple('UILang', ['code', 'englishName', 'nativeName', 'localeName', 'nsisName', 'crowdinId'], defaults=[None])

# The code of the source (untranslated) language. English is the language the UI strings are written in, so it has no .ts/.qm files, no translated XXE addon, and no Crowdin entry.
SOURCE_CODE = 'en'

# The authoritative list. Order matters in one place: it is the top-to-bottom order of the installer's language-picker dialog (via the generated languages.nsh).
LANGUAGES = [
    UILang(code='en', englishName='English', nativeName='English',  localeName='en_US', nsisName='English'),
    UILang(code='es', englishName='Spanish', nativeName='Español',  localeName='es_ES', nsisName='Spanish', crowdinId='es-ES'),
    UILang(code='fr', englishName='French',  nativeName='Français', localeName='fr_FR', nsisName='French'),
    UILang(code='de', englishName='German',  nativeName='Deutsch',  localeName='de_DE', nsisName='German'),
]

def forCode(code):
    '''Return the UILang record for a two-letter code, or None if the code isn't a supported UI language.'''

    for lang in LANGUAGES:

        if lang.code == code:
            return lang

    return None

def allCodes():
    '''Every supported UI-language code, including English.'''

    return [lang.code for lang in LANGUAGES]

def translationCodes():
    '''The codes of the translation languages — every UI language except English (the source language). These are the codes that have _XX.ts/.qm files, translated XXE addons, etc.'''

    return [lang.code for lang in LANGUAGES if lang.code != SOURCE_CODE]

def englishNameForCode(code, default='English'):
    '''The English name of the language with the given code (e.g. 'de' -> 'German'), or `default` for an unknown code.'''

    lang = forCode(code)
    return lang.englishName if lang else default

def nativeNameForCode(code, default=''):
    '''The language's name in itself (e.g. 'de' -> 'Deutsch'), or `default` for an unknown code.'''

    lang = forCode(code)
    return lang.nativeName if lang else default

def localeNameForCode(code):
    '''The locale name (e.g. 'de_DE') for date/time formatting in the given language, or None for an unknown code (callers fall back to the system default locale).'''

    lang = forCode(code)
    return lang.localeName if lang else None
