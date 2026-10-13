#
#   ChapterSelection
#
#   Ron Lockwood
#   SIL International
#   5/3/22
#
#   Version 3.17.7 - 10/12/26 - Ron Lockwood
#    Fixes #1623. Export offers to create a missing book file, with an \id line and chapter placeholders. Clearer book-not-found message. Fixed splicing into empty chapters.
#    All book data (order, names, chapter counts) now lives in one BOOKS table, which names all 123 Paratext books.
#    Read .vrs book lines that end in END, and cache the chapter counts read from .vrs files.
#
#   Version 3.17.6 - 10/7/26 - Ron Lockwood
#    Cluster projects use the alternate Paratext folder: added getProjectFolder() (book files directly in the folder or in a per-project subfolder)
#    and getParatextProjects() lists the alternate folder's projects. Updated the code description block for the separate import and export settings.
#
#   Version 3.17.5 - 9/29/26 - Ron Lockwood
#    Fixes #1235. Import option to put numbers in the analysis WS, with a box for the number separator character(s).
#
#   Version 3.17.4 - 9/8/26 - Ron Lockwood
#    Allow for the bidi control marks that right-to-left text puts beside the punctuation of a verse reference, in every reference pattern in splitSFMs.
#
#   Version 3.17.3 - 9/8/26 - Ron Lockwood
#    Fixes #1546. Handle comma-separated verse ranges after a verse reference with a dash, e.g. 17:26-30, 34-36, 41, 
#    ranges that cross a chapter boundary, e.g. 1:2-3:4, and non-ASCII commas such as the Arabic one.
#
#   Version 3.17.2 - 9/2/26 - Ron Lockwood
#    Added a code description block at the top with an overview, key features and code structure.
#
#   Version 3.17.1 - 9/2/26 - Ron Lockwood
#    Made the Paratext chapter selection window a fixed size so the user can't resize it to where controls get clipped.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.3 - 7/29/26 - Ron Lockwood
#    Put the FLExTrans icon on the overwrite-chapters message box.
#
#   Version 3.16.2 - 7/22/26 - Ron Lockwood
#    Fixes #1461. Make sure a blank writing system isn't used to create a text in FLEx.
#
#   Version 3.16.1 - 6/30/26 - Ron Lockwood
#    Fixes #1397. Shortened file paths shown in user messages with Utils.shortenPathForDisplay().
#
#   Version 3.16 - 6/24/26 - Ron Lockwood
#    Added an optional vernWs parameter to insertParagraphs so One project mode can insert text into a chosen vernacular writing system.
#
#   Version 3.15.5 - 6/20/26 - Ron Lockwood
#    Fixes #1353. On export, overwrite the Paratext book's \id line with the one carried in the text (if present).
#
#   Version 3.15.4 - 6/20/26 - Ron Lockwood
#    Fixes #1353. Keep the whole \id book-identifier line in the Vernacular WS when inserting paragraphs.
#
#   Version 3.15.3 -4/17/26 - Ron Lockwood
#    Fixes #1312. Translate book names when checking for valid names.
#
#   Version 3.15.2 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15.1 - 2/11/26 - Ron Lockwood
#    Fixes #1149. Support alternate Paratext folder setting.
#
#   Version 3.15 - 2/9/26 - Ron Lockwood
#    Fixes #1232. Change regex for attributes to stop matching on a backslash. This prevents
#    it from matching across multiple figures in a book.
#
#   Version 3.14.3 - 12/10/25 - Ron Lockwood
#    Fixes #1143. Allow .USFM files as well as .SFM files.
#
#   Version 3.14.2 - 12/3/25 - Ron Lockwood
#    Refixes #1139. Reword the error message.
#
#   Version 3.14.1 - 12/3/25 - Ron Lockwood
#    Fixes #1139. Give a better error message when Paratext path is not found in registry.
#
#   Version 3.14 - 5/29/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.3 - 6/6/25 - Ron Lockwood
#    Fixes #1004. Handle any kind of unicode dash in verse references.
#
#   Version 3.13.2 - 4/22/25 - Ron Lockwood
#    Fixes #967. Handle \xt until \xt*. Sometimes \xt gets terminated with \x* and sometimes with \xt*.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.8 - 3/4/25 - Ron Lockwood
#    Fixes #903. Don't show the 'Don't show message again' checkbox if there are no cluster projects.
#
#   Version 3.12.7 - 1/23/25 - Ron Lockwood
#    Support import of Glossary book (GLO).
#
#   Version 3.12.6 - 1/15/25 - Ron Lockwood
#    Export from the target DB as the default. Also recognize texts that have - Copy ...
#    at the end.
#
#   Version 3.12.5 - 1/15/25 - Ron Lockwood
#    Export from FLEx to Paratext, optionally across cluster projects.
#
#   Version 3.12.4 - 1/13/25 - Ron Lockwood
#    Fixes crash on import with no cluster projects.
#
#   Version 3.12.3 - 12/31/24 - Ron Lockwood
#    Fixes #830. Track the Paratext path instead of book path.
#
#   Version 3.12.2 - 12/30/24 - Ron Lockwood
#    Support for importing cluster projects.
#
#   Version 3.12.1 - 11/26/24 - Ron Lockwood
#    Allow intro. to be imported with chapter 1.
#
#   Version 3.10.1 - 3/19/24 - Ron Lockwood
#    Fixes #566. Allow the user to create one text per chapter when importing.
#
#   Version 3.10 - 3/13/24 - Ron Lockwood
#    Support Paratext lexicon import.
#
#   2023 version history removed on 2/6/26
#
#   OVERVIEW (AI generated, then edited)
#
#   This library holds what the three Paratext chapter modules have in common: the ChapterSelection class that carries the user's choices around, the code behind the Choose Chapters window that all
#   three of them put up, the map of Paratext book abbreviations to book names, the marker aware code that turns Paratext text into FLEx paragraphs, and doExport() which splices chapters back into a
#   Paratext book file. The three modules are Import From Paratext, Export FLExTrans Draft to Paratext and Export Text from Target FLEx to Paratext. Each one builds the window from
#   Lib/Windows/ParatextChapSelectionDlg.ui, hands it to InitControls() to be filled in and fitted to the job, and once the user clicks OK reads the ChapterSelection object back off the window.
#
#   Paratext itself is found through the registry. getParatextPath() reads the Settings_Directory value under SOFTWARE\Wow6432Node\Paratext\8, and getParatextProjects() lists the project folders
#   under it, skipping cms, Temp Files and anything starting with an underscore or UserSettings. An alternate folder overrides that whole scheme when it is set, which is how a module can work
#   against a folder of book files that isn't a Paratext installation. There are two such settings, one for importing (AlternateParatextFolder) and one for exporting (AlternateParatextExportFolder);
#   each module reads the one it needs and passes it to getParatextProjects() and doOKbuttonValidation() as altParatextFolder, so nothing in this file knows which direction it is.
#
#   getProjectFolder() decides where a project's book files live. Without an alternate folder that is <Paratext data folder>\<project>. With one, it is <alternate folder>\<project> if that
#   subfolder exists, otherwise the alternate folder itself. Supporting both layouts is what lets cluster projects work from an alternate folder: either it is a copy of a whole Paratext projects
#   folder with one subfolder per project, or every project's book files sit side by side in it and the project abbreviation in each file name tells them apart. getParatextProjects() lists the
#   alternate folder's projects for the cluster combo boxes the same two ways - subfolders holding book files, plus the project abbreviations read out of the book file names (getBookFileProjects).
#   getBookPath() finds the book file itself in the project folder through findBookFile(). If the folder is a real Paratext project, its Settings.xml has a <Naming> element (e.g. PostPart="ABC.SFM"
#   BookNameForm="41MAT") that gives the exact file name, so that is tried first. Otherwise it looks for *<book><project>.SFM and then *<book><project>.USFM. The * matches the book number, which
#   some projects leave out of their file names. When nothing is found, getBookNotFoundMessage() names the book, the project, a file name of the right shape and the folder, never the wildcard pattern.
#
#   BOOK NUMBERS AND NEW BOOK FILES
#
#   The number at the front of a Paratext book file name comes from the book's place in Paratext's canonical order (PARATEXT_BOOK_ORDER), not from how many books a project has. getParatextBookNumStr()
#   applies Paratext's quirks: 01-39 for the Old Testament, then 40 is skipped so Matthew is 41, counting up to 100 for XXG, then A0-A9, B0-B9 and C0-C3 for FRT onward. getNewBookFileName() names a
#   new book file the way the project already names its books: from Settings.xml if there is one, otherwise like the project's other book files in the folder (number or no number, .SFM or .USFM),
#   otherwise Paratext's default <number><book><project>.SFM. createBookFile() writes the \id line and an empty chapter placeholder (\c 1, \c 2, ...) for every chapter of the book.
#   getBookChapterCount() gets the number of chapters from the project's versification: the <Versification> number in Settings.xml names one of the standard .vrs files Paratext keeps in its projects
#   folder (VERSIFICATION_FILES), a custom.vrs in the project folder overrides the books it lists, and when neither can be found the built-in English counts (ENGLISH_CHAPTER_COUNTS) are used.
#   readVrsChapterCounts() only takes the book lines (allowing the END some custom.vrs files put at the end of them) and skips the verse mapping lines. It caches what it reads in
#   vrsChapterCountsCache so each file is parsed only once per session (an edit made while FlexTools is running isn't seen); the cached dicts are shared, so nothing may change them.
#   markBookPresent() sets the book's flag in Settings.xml's <BooksPresent> string (one 0/1 per book in canonical order) so Paratext shows the book. That edit is done on the text, not by rewriting
#   the XML, so the byte order mark, the CRLF line endings and everything else in Paratext's file stay as they were.
#
#   THE WINDOW
#
#   One dialog serves all three modules and InitControls() is what makes it fit the module that opened it. It loads the settings from last time, then hides what doesn't apply. For either export the
#   import-only checkboxes go away (footnotes, cross references, make active, full book name, one text per chapter, include introduction, overwrite existing text, and numbers in the analysis
#   writing system with its number separator box) and the window shrinks by EXP_SHRINK_WINDOW_PIXELS. Exporting from FLEx additionally hides the book abbreviation and the two chapter spin
#   boxes, because that information comes from the text titles the user picks instead, and gives FROM_FLEX_EXP_PIXELS of that shrink back. Anything that isn't exporting from FLEx hides the
#   scripture texts combo box and its label. Cluster project rows are only set up for importing and for exporting from FLEx; the other module hides them. Two of the combo boxes are swapped at
#   runtime for a CheckableComboBox (here for scripture texts, in ClusterUtils for cluster projects) so the user can check several entries instead of picking one. The number separator box
#   is only enabled while its checkbox is checked (enableNumberSeparator()).
#
#   The controls in the .ui file are placed with absolute geometry rather than Qt layouts, so the window has no idea what size it needs and resizing it doesn't rearrange anything - it just clips
#   controls out of view. That is why the size is pinned: lockWindowSize() fixes the window at whatever size was just laid out, unlockWindowSize() lifts the pin so code can resize the window again,
#   and showClusterWidgets() wraps the ClusterUtils call in that unpin and repin because the window grows and shrinks by a row every time the user checks or unchecks a cluster project.
#
#   doOKbuttonValidation() is the OK handler for all three windows. It reads every control, then validates as much as it can: the book abbreviation has to be in bookMap, the Paratext path has to
#   have come out of the registry and exist, the project folder under it has to exist and (when importing) the book file has to be there. With cluster projects selected, the project and book checks
#   are skipped here, since each project has its own Paratext project and gets checked as it is processed. If everything passes it builds the ChapterSelection object, saves the settings and closes
#   the window with retVal set to True. Every validation failure puts up a message box and leaves the window open.
#
#   THE SETTINGS FILE
#
#   The user's choices are remembered in ParatextImportSettings.json, in the same Config folder as flextools.ini. ChapterSelection.dump() defines what goes in it and doOKbuttonValidation() writes
#   it. The one subtlety is that the file holds both an export project abbreviation and an import project abbreviation. Whichever one the running module isn't using is carried through untouched in
#   the window's otherProj member, so that importing doesn't wipe out the project the user exports to, or the other way around.
#
#   BOOK NAMES AND TEXT TITLES
#
#   Everything known about a book lives in one table, BOOKS, at the bottom of the file: one row per Paratext book, in canonical order, giving its abbreviation, its name and its chapter count in the
#   English versification. PARATEXT_BOOK_ORDER, bookMap and ENGLISH_CHAPTER_COUNTS are all derived from it, so a book is only ever changed in one place. Because a row's position is the book's Paratext
#   number, rows must never be reordered, inserted or removed. bookMap maps each abbreviation to its book name, and the names go through _translate() so they come out in the UI language. It covers all
#   123 books Paratext knows about: the 66 books, the deuterocanonical books, the alternate Greek forms (JSA, DNT, ...) and the peripheral books (FRT, GLO, CNC, ...). The peripheral books have no
#   chapters, so the chapter-based import and export can't do much with them. bookChapterPattern parses a FLEx text title into a book part and one or two two-digit chapter numbers, and tolerates a
#   trailing " - Copy" or " - Copy (2)" that FLEx adds when a title is duplicated. getScriptureText() uses it to filter a project's text titles down to the ones that look like scripture: the book part
#   has to be an abbreviation or a book name in either English or the UI language. Comparisons normalize to decomposed Unicode (NFD) because that is how FLEx stores text.
#
#   MARKERS AND WRITING SYSTEMS
#
#   insertParagraphs() is what actually puts Paratext text into a FLEx text, and the writing systems matter as much as the text does. splitSFMs() splits the string into markers and references on one
#   side and text content on the other; the markers and references are put in the Analysis writing system so FLEx doesn't ask the user to interlinearize them, and the content goes in the Vernacular
#   writing system (or, in One project mode, whichever vernacular writing system the caller passes in). Its regular expression is long because every marker shape has to be recognized - end markers,
#   footnotes and their references, cross references, verses and verse ranges, chapters, attributes running from a vertical bar to a closing marker, and markers preceded by a plus. The \id book
#   identifier is the deliberate exception: it stays in the Vernacular writing system so the book id survives translation and can be written back on export. A new FLEx paragraph is started at every
#   line feed. When the user checks "Import numbers in the analysis writing system", splitNumbers() goes over each piece of text content and pulls out free-standing numbers - digits optionally
#   grouped by the characters in the Number separator(s) box, like 144,000 - so they go in the Analysis writing system too. A separator only counts when a digit follows it, so the comma after a
#   number at the end of a clause stays vernacular punctuation, and digits touching letters (e.g. 7th) are left alone as part of a word. convertFigSyntax() rewrites the old USFM 1.0 and 2.0 \fig
#   syntax into the 3.0 form, and setTextMetaData() marks a created text with Source of FLExTrans and IsTranslated.
#
#   SPLICING CHAPTERS BACK INTO A PARATEXT BOOK
#
#   doExport() is the export half, shared by both export modules. It first looks for the book file. If the project doesn't have the book yet, askToCreateBookFile() asks whether to create it (in the
#   standard Paratext folder or the alternate one alike) and creates it on a yes. It always asks, so a mistyped project doesn't quietly leave a stray file behind. A new book skips the overwrite
#   question and the backup, since there is nothing in it yet. For an existing book it asks the user to confirm overwriting the chapters it found in the text, offering a do-not-ask-again checkbox when
#   cluster projects are in play so the question only has to be answered once. Then it backs the book file up to <book>.bak, and if the incoming text carries an \id line (import put it there) that
#   line replaces the book's own \id line. For a new book the intro that comes along with chapter 1 has its \id line stripped, because the file already starts with one. The incoming text is split on
#   \c markers and each chapter is dealt with on its own: if the book already has that chapter, the text from that \c marker up to the next one (or to the end of the file for the last chapter) is
#   replaced; if it doesn't, the chapter is inserted ahead of the next higher chapter in the book; and if there is no higher chapter it is appended. A new book's placeholders mean every exported
#   chapter takes the first path. Chapters can be empty - a placeholder, or an empty chapter Paratext made - so a chapter's old contents are matched with .*? up to a lookahead for the next \c
#   <number>, not .+? up to \c, which swallowed the next marker after an empty chapter and also stopped at \cp or \cl. (?!\d) after the chapter number keeps \c 2 from matching \c 20. Backslashes in
#   the replacement text are doubled first, because re.sub() would otherwise read them as group references.
#
#   CODE STRUCTURE
#
#   Top to bottom the file goes: the constants (bookChapterPattern, PARATEXT_SETTINGS_FILE, VERSIFICATION_FILES, vrsChapterCountsCache), the ChapterSelection class with its dump(), getBookFolder(),
#   getBookPath() and getBookNotFoundMessage(), the marker and paragraph functions (splitSFMs, splitNumbers, convertFigSyntax, insertParagraphs, setTextMetaData), the window functions (lockWindowSize,
#   unlockWindowSize, showClusterWidgets, enableNumberSeparator, InitControls), getParatextPath, doOKbuttonValidation, the project and book file helpers (getFilteredSubdirectories, getProjectFolder,
#   getParatextBookNumStr, getProjectSettingsRoot, getProjectNaming, makeBookFileName, findBookFile, getNewBookFileName, getBookNotFoundMessage, markBookPresent, readVrsChapterCounts,
#   getBookChapterCount, createBookFile, askToCreateBookFile, getBookFileProjects, getParatextProjects), getScriptureText, doExport, and finally the module level QApplication and translator setup
#   followed by BOOKS and the three things derived from it (PARATEXT_BOOK_ORDER, bookMap, ENGLISH_CHAPTER_COUNTS). BOOKS has to come after the translations are loaded, which is why the biggest thing
#   in the file is also the last thing in it. The functions that use the book data only read it when they're called, so it doesn't matter that they come first.
#

import os
import regex as re
import unicodedata
from shutil import copyfile
import winreg
import glob
import json
import codecs
import xml.etree.ElementTree as ET
from typing import cast

from PyQt6.QtWidgets import QMessageBox, QCheckBox, QApplication, QWIDGETSIZE_MAX
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon

import ClusterUtils
from ComboBox import CheckableComboBox
import FTPaths
import Utils
from SIL.LCModel.Core.Text import TsStringUtils         # type: ignore

# Define _translate for convenience
_translate = QCoreApplication.translate

PTXIMPORT_SETTINGS_FILE = 'ParatextImportSettings.json'
EXP_SHRINK_WINDOW_PIXELS = 142
DEFAULT_NUMBER_SEPARATORS = ','
FROM_FLEX_EXP_PIXELS = 33

bookChapterPattern = re.compile(r'^(?P<book>.+?) (?P<chap1>\d{2})(?:-(?P<chap2>\d{2}))?(?: - Copy(?: \(\d{1,2}\))?)?$')

# The file in a Paratext project folder that holds the project's settings, including how its book files are named (<Naming>) and which books it has (<BooksPresent>)
PARATEXT_SETTINGS_FILE = 'Settings.xml'

# The standard versification files Paratext keeps in its projects folder, keyed by the number in a project's Settings.xml <Versification> element
VERSIFICATION_FILES = {'1': 'org.vrs', '2': 'lxx.vrs', '3': 'vul.vrs', '4': 'eng.vrs', '5': 'rsc.vrs', '6': 'rso.vrs'}

# Chapter counts already read from .vrs files, so each file is parsed only once per session: {normalized path: {book: chapter count}}. See readVrsChapterCounts().
vrsChapterCountsCache = {}

class ChapterSelection(object):
        
    def __init__(self, export, otherProj, projectAbbrev, bookAbbrev, paratextPath, fromChap, toChap, includeFootnotes, includeCrossRefs, \
                 makeActive, useFullBookName, overwriteText, clusterProjects, ptxProjList, oneTextPerChapter=False, includeIntro=False, altParatextFolder=None, \
                 numbersAsAnalysis=False, numberSeparators=DEFAULT_NUMBER_SEPARATORS):
    
        self.export = export
        self.dontShowWarning = False
        self.overwriteAllChapters = False
        self.confirmContinueOverwrite = False

        if self.export:
            self.exportProjectAbbrev = projectAbbrev  
            self.importProjectAbbrev = otherProj   
        else:
            self.importProjectAbbrev = projectAbbrev  
            self.exportProjectAbbrev = otherProj   

        self.bookAbbrev         = bookAbbrev  
        self.paratextPath       = paratextPath   
        self.altParatextFolder  = altParatextFolder  
        self.fromChap           = fromChap        
        self.toChap             = toChap          
        self.includeFootnotes   = includeFootnotes
        self.includeCrossRefs   = includeCrossRefs
        self.makeActive         = makeActive      
        self.useFullBookName    = useFullBookName  
        self.overwriteText      = overwriteText
        self.clusterProjects    = clusterProjects   
        self.ptxProjList        = ptxProjList
        self.oneTextPerChapter  = oneTextPerChapter
        self.includeIntro       = includeIntro
        self.numbersAsAnalysis  = numbersAsAnalysis
        self.numberSeparators   = numberSeparators

    def dump(self):
        
        ret = {\
            'exportProjectAbbrev'    : self.exportProjectAbbrev,
            'importProjectAbbrev'    : self.importProjectAbbrev,
            'bookAbbrev'             : self.bookAbbrev,
            'fromChap'               : self.fromChap,
            'toChap'                 : self.toChap,
            'includeFootnotes'       : self.includeFootnotes,
            'includeCrossRefs'       : self.includeCrossRefs,
            'makeActive'             : self.makeActive,
            'useFullBookName'        : self.useFullBookName,
            'oneTextPerChapter'      : self.oneTextPerChapter,
            'includeIntro'           : self.includeIntro,
            'overwriteText'          : self.overwriteText,
            'numbersAsAnalysis'      : self.numbersAsAnalysis,
            'numberSeparators'       : self.numberSeparators,
            'clusterProjects'        : self.clusterProjects,
            'ptxProjList'            : self.ptxProjList,
            }
        return ret
    
    def getProjectAbbrev(self):

        if self.export:
            return self.exportProjectAbbrev
        else:
            return self.importProjectAbbrev

    def getBookFolder(self):

        return getProjectFolder(self.paratextPath, self.altParatextFolder, self.getProjectAbbrev())

    def getBookPath(self):

        return findBookFile(self.getBookFolder(), self.bookAbbrev, self.getProjectAbbrev())

    def getBookNotFoundMessage(self):

        return getBookNotFoundMessage(self.getBookFolder(), self.bookAbbrev, self.getProjectAbbrev())

# Commas that can separate the parts of a verse list, e.g. the one in 17:26-30, 34-36. Unicode has no comma property to match, so the commas are spelled out instead. 
# The Arabic comma is the one that matters most for right-to-left scripts -- Arabic, Persian, Urdu, Pashto, Sindhi, Uyghur and Thaana all use it -- and the
# N'Ko and reversed commas are right-to-left as well. The Arabic decimal separator U+066B is deliberately left out.
ANY_COMMA = r'[,\u060C\u066C\u07F8\u2E41\u1363\u055D\u3001\uFF0C\uFE10\uFE11\uFE50\uFE51\u1802\u1808\uA4FE]'

# Right-to-left Scripture text puts an invisible bidi control character next to the punctuation of a verse reference, so a Farsi or Urdu parallel reference reads 13<RLM>:32<RLM><EN DASH>37 rather than
# 13:32-37. Those marks are real characters sitting between the digits and the separator, so without allowing for them here not one reference in such a line is recognised and the whole line, verse
# numbers and all, is handed to the interlinearizer as vernacular text. \p{Bidi_Control} is the Unicode property for exactly these twelve: the marks (ALM, LRM, RLM), the embeddings and overrides
# (U+202A-U+202E) and the isolates (U+2066-U+2069). They are allowed on both sides of every separator because which side they fall on is up to whoever typed the text.
BIDI_MARKS = r'\p{Bidi_Control}*'

# The separators of a verse reference, each able to carry bidi marks: the chapter/verse separator, the dash in a range, and the comma between the parts of a verse list.
CV_SEP = BIDI_MARKS + r'[:.]' + BIDI_MARKS
RANGE_DASH = BIDI_MARKS + r'[\p{Pd}]' + BIDI_MARKS
LIST_COMMA = BIDI_MARKS + ANY_COMMA + r' ?' + BIDI_MARKS

# Split the text into sfm marker (or ref) and non-sfm marker (or ref), i.e. text content. The sfm marker or reference will later get marked as analysis lang. so it doesn't
# have to be interlinearized. Always put the marker + ref with dash before the plain marker + ref. \\w+* catches all end markers and \\w+ catches everything else (it needs to be at the end)
# We have the \d+:\d+-\d+ and \d+:\d+ as their own expressions to catch places in the text that have a verse reference like after a \r or \xt. It's nice if these get marked as analysis WS.
# Attributes are of the form |x=123 ... \s*
# You can't have parens inside of the split expression since the whole thing is already in parens, unless you mark it as non-capturing parens with ?:. Otherwise it will mess up the output.
def splitSFMs(inputStr):

    segs = re.split(r'(\n|'                 # newline
                    r'\|\w+?=(?:.|\n)+?\*|' # attributes (|xyz=...) ending in * but possibly across lines
                    r'\||'                  # verticle bar
                    r'\\\w+\*|'             # end marker
                    r'\\f \+ |'             # footnote with plus
                    r'\\fr \d+' + CV_SEP + r'\d+' + RANGE_DASH + r'\d+|' # footnote reference with dash (either colon or dot separating chapter and verse)
                                            # RANGE_DASH is any unicode dash (property=Pd) and CV_SEP is the colon or dot, and each also allows the bidi control marks that right-to-left text puts beside them.
                    r'\\fr \d+' + CV_SEP + r'\d+|'     # footnote reference
                    r'\\xt .+?\\xt\*|'      # target reference until target reference end marker
                    r'\\xt .+?\\x\*|'       # target reference until cross reference end marker
                    r'\\x \+ |'             # cross reference with plus
                    r'\\xo \d+' + CV_SEP + r'\d+' + RANGE_DASH + r'\d+|' # origin reference with dash
                    r'\\xo \d+' + CV_SEP + r'\d+|'     # origin reference normal
                    r'\\v \d+' + RANGE_DASH + r'\d+ |' # verse with dash
                    r'\\v \d+ |'            # verse
                    r'\\vp \S+ |'           # publication verse
                    r'\\c \d+|'             # chapter
                    r'\\rem.+?\n|'          # remark
                    r'\\id.+?\n|'           # book identifier
                                            # verse reference with dash, followed by any comma-separated verse ranges or lone verses, e.g. 17:26-30, 34-36, 39-40, 41
                                            # The optional (?:[:.]\d+)? lets the range end at a full chapter:verse rather than a bare verse number, 
                                            # so a range that crosses a chapter boundary like 1:2-3:4 is kept whole instead of breaking after 1:2-3 and leaving :4 to be treated as vernacular text.
                                            # The possessive \d++ plus the (?![:.]) lookahead stop the comma list at something like ', 18:1' -- that's a new chap:ver ref. and gets split off on its own.
                    r'\d+' + CV_SEP + r'\d+' + RANGE_DASH + r'\d+(?:' + CV_SEP + r'\d+)?(?:' + LIST_COMMA + r'\d++(?:' + RANGE_DASH + r'\d++)?(?!' + BIDI_MARKS + r'[:.]))*|' 
                    r'\d+' + CV_SEP + r'\d+|'          # verse reference
                    r'\\\+\w+|'             # marker preceded by plus
                    r'\\\w+)',              # any other marker
                    inputStr) 
    return segs

# Split a piece of text content (no markers or references in it) into text and numbers, so numbers can be put in the analysis WS. Like re.split with a capturing group, the result alternates
# text, number, text, ..., so the odd-numbered items are the numbers. A number is a run of digits optionally grouped by any of the characters in numberSeparators, e.g. 7, 144,000 or 1.000.000.
# A separator only counts when a digit follows it, so the comma in "7, and" stays with the text. The lookarounds keep digits that touch letters (e.g. 7th or 144,000th) as part of the word.
def splitNumbers(inputStr, numberSeparators):

    # Build a character class out of the separators the user gave. Escape each one so that characters like - or ] can't change the meaning of the class. The quantifiers are possessive
    # (++ and *+) so that when a whole number is followed by letters the engine can't back off to a shorter match: without that, 144,000th would give up ",000th" and match 144 on its own.
    if numberSeparators:

        # The regex stubs type escape() as returning bytes | str even for a str argument. numberSeparators always comes from the window's line edit, so it's a str and so is the result.
        separatorClass = '[' + ''.join(cast(str, re.escape(sepChar)) for sepChar in numberSeparators) + ']'
        numberPattern = r'(?<!\w)(\d++(?:' + separatorClass + r'\d++)*+)(?!\w)'
    else:
        numberPattern = r'(?<!\w)(\d++)(?!\w)'

    return re.split(numberPattern, inputStr)

# Convert old USFM 1.0 or 2.0 \fig syntax to 3.0. 
# old format: \fig DESC|FILE|SIZE|LOC|COPY|CAP|REF\fig*
# new format: \\fig CAP|alt="DESC" src="FILE" size="SIZE" loc="LOC" copy="COPY" ref="REF"\\fig*
def convertFigSyntax(importText):

    return re.sub(r'\\fig ([^\\|]*)\|([^\\|]*)\|([^\\|]*)\|([^\\|]*)\|([^\\|]*)\|([^\\|]*)\|([^\\|]*)\\fig\*', 
                  r'\\fig \6|alt="\1" src="\2" size="\3" loc="\4" copy="\5" ref="\7"\\fig*', importText)

def insertParagraphs(DB, inputStr, m_stTxtParaFactory, stText, vernWs=None, numbersAsAnalysis=False, numberSeparators=DEFAULT_NUMBER_SEPARATORS):

    # In One project mode the synthesized text is inserted into a chosen (secondary) vernacular writing system rather than the
    # project's default vernacular WS. Callers pass that WS handle in vernWs; otherwise fall back to the default vernacular WS.
    if vernWs is None:

        vernWs = DB.project.DefaultVernWs
        assert vernWs, "Default vernacular writing system is not set in the target project."

    # Fix any sfms that are split across two lines. E.g. kanqa>>.\[newline]x + \xo ...
    # put the \ after the newline
    inputStr = re.sub(r'\\\n', r'\n\\', inputStr)

    segs = splitSFMs(inputStr)

    # Create 1st paragraph object
    stTxtPara = m_stTxtParaFactory.Create()
    
    # Add it to the stText object
    stText.ParagraphsOS.Add(stTxtPara)    
    bldr = TsStringUtils.MakeStrBldr()

    # Start a new paragraph at every line feed
    newPar = r'\n' 
    
    for _, seg in enumerate(segs):
        
        if not (seg is None or len(seg) == 0 or seg == '\n'):
            
            # Either an sfm marker or a verse ref should get marked as Analysis WS. The exception is the \id book-identifier
            # marker, whose whole line (marker included) must stay in the Vernacular WS so the book id travels through translation.
            if re.search(r'\\|\d+[.:]\d+', seg) and seg != '\\id':

                # make this in the Analysis WS
                tss = TsStringUtils.MakeString(re.sub(r'\n','', seg), DB.project.DefaultAnalWs)
                bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
                
            # If the user wants numbers in the Analysis WS, split them out of the text content. splitNumbers alternates text and number, so odd-numbered pieces are numbers.
            elif numbersAsAnalysis:

                for i, piece in enumerate(splitNumbers(re.sub(r'\n','', seg), numberSeparators)):

                    if not piece:

                        continue

                    pieceWs = DB.project.DefaultAnalWs if i % 2 == 1 else vernWs
                    tss = TsStringUtils.MakeString(piece, pieceWs)
                    bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
            else:
                # make this in the Vernacular WS (the chosen target WS in One project mode, otherwise the default vernacular WS)
                tss = TsStringUtils.MakeString(re.sub(r'\n','', seg), vernWs)
                bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
        
        if seg and re.search(newPar, seg): # or first segment if not blank
        
            # Save the built up string to the Contents member
            stTxtPara.Contents = bldr.GetString()
            
            # Create paragraph object
            stTxtPara = m_stTxtParaFactory.Create()
            
            # Add it to the stText object
            stText.ParagraphsOS.Add(stTxtPara)  
        
            bldr = TsStringUtils.MakeStrBldr()
        
    stTxtPara.Contents = bldr.GetString()

def setTextMetaData(DB, text):

    # Set the Source field
    tss = TsStringUtils.MakeString('FLExTrans', DB.project.DefaultAnalWs)
    text.Source.AnalysisDefaultWritingSystem = tss

    # Set the IsTranslated field
    text.IsTranslated = True

def lockWindowSize(self):

    # All the controls in the chapter selection window are placed with absolute geometry (there are no layouts), so resizing the window doesn't rearrange anything. Shrinking it clips
    # whatever is near the bottom and right edges out of view and enlarging it just adds empty space, so pin the window to the size we laid out for the controls that are showing.
    self.setFixedSize(self.width(), self.height())

def unlockWindowSize(self):

    # Lift the pinning from lockWindowSize so the window can be resized in code again. Without this, a resize call would be clamped to the size that was pinned last.
    self.setMinimumSize(0, 0)
    self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)

def showClusterWidgets(self):

    # ClusterUtils resizes the window to fit however many cluster project rows are showing, so the window has to be unpinned while it does that. Then pin the new size.
    unlockWindowSize(self)
    ClusterUtils.showClusterWidgets(self)
    lockWindowSize(self)

def enableNumberSeparator(self, enable):

    self.ui.numberSeparatorLabel.setEnabled(enable)
    self.ui.numberSeparatorLineEdit.setEnabled(enable)

def InitControls(self, export=True, fromFLEx=False):
    
    self.chapSel = None
    self.retVal = False
    
    self.ui.OKButton.clicked.connect(self.OKClicked)
    self.ui.CancelButton.clicked.connect(self.CancelClicked)

    # Set initial window size. Import doesn't change it (but in ClusterUtils height is saved), but export to ptx and export from flex do.
    self.otherProj = ''
    self.resize(ClusterUtils.IMP_EXP_WINDOW_WIDTH, ClusterUtils.IMP_EXP_WINDOW_HEIGHT)
    
    # Load settings if available
    try:
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add the settings file
        self.settingsPath = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), PTXIMPORT_SETTINGS_FILE)
        
        f = open(self.settingsPath, 'r')
        myMap = json.load(f)
        f.close()
    except:
        myMap = {}
        
    # Set the project edit box to either the export or import project.
    # Save the other one as otherProj so we can write it out again to the settings file.
    if export:
        self.ui.ptxProjAbbrevLineEdit.setText(myMap.get('exportProjectAbbrev',''))
        self.otherProj = myMap.get('importProjectAbbrev','')
    else:
        self.ui.ptxProjAbbrevLineEdit.setText(myMap.get('importProjectAbbrev',''))
        self.otherProj = myMap.get('exportProjectAbbrev','')
        
    self.ui.bookAbbrevLineEdit.setText(myMap.get('bookAbbrev',''))
    self.ui.fromChapterSpinBox.setValue(myMap.get('fromChap',1))
    self.ui.toChapterSpinBox.setValue(myMap.get('toChap',1))
    self.ui.footnotesCheckBox.setChecked(myMap.get('includeFootnotes',False))
    self.ui.crossrefsCheckBox.setChecked(myMap.get('includeCrossRefs',False))
    self.ui.makeActiveTextCheckBox.setChecked(myMap.get('makeActive',True))
    self.ui.useFullBookNameForTitleCheckBox.setChecked(myMap.get('useFullBookName',True))
    self.ui.oneTextPerChapterCheckBox.setChecked(myMap.get('oneTextPerChapter',False))
    self.ui.includeIntroCheckBox.setChecked(myMap.get('includeIntro',False))
    self.ui.overwriteExistingTextCheckBox.setChecked(myMap.get('overwriteText',False))
    self.ui.numberSeparatorLineEdit.setText(myMap.get('numberSeparators', DEFAULT_NUMBER_SEPARATORS))

    # The number separator box only means something when numbers are going into the analysis WS, so keep it (and its label) enabled only while that checkbox is checked.
    self.ui.numbersAsAnalysisCheckBox.toggled.connect(lambda checked: enableNumberSeparator(self, checked))
    self.ui.numbersAsAnalysisCheckBox.setChecked(myMap.get('numbersAsAnalysis',False))
    enableNumberSeparator(self, self.ui.numbersAsAnalysisCheckBox.isChecked())

    # Change widgets if we are doing export
    if export:

        # Hide the checkboxes
        self.ui.footnotesCheckBox.setVisible(False)
        self.ui.crossrefsCheckBox.setVisible(False)
        self.ui.makeActiveTextCheckBox.setVisible(False)
        self.ui.useFullBookNameForTitleCheckBox.setVisible(False)
        self.ui.oneTextPerChapterCheckBox.setVisible(False)
        self.ui.includeIntroCheckBox.setVisible(False)
        self.ui.overwriteExistingTextCheckBox.setVisible(False)
        self.ui.numbersAsAnalysisCheckBox.setVisible(False)
        self.ui.numberSeparatorLabel.setVisible(False)
        self.ui.numberSeparatorLineEdit.setVisible(False)

        pixels = EXP_SHRINK_WINDOW_PIXELS

        if fromFLEx:

            self.ui.bookAbbrevLineEdit.setVisible(False)
            self.ui.bookAbbrevLabel.setVisible(False)
            self.ui.fromChapterSpinBox.setVisible(False)
            self.ui.toChapterSpinBox.setVisible(False)
            self.ui.chapterLabel.setVisible(False)
            self.ui.toLabel.setVisible(False)

            pixels -= FROM_FLEX_EXP_PIXELS

        # Resize the main window 
        self.resize(self.width(), self.height()-pixels)

        # Move controls up by pixels
        widgetsToMove = [
            self.ui.clusterProjectsLabel,
            self.ui.clusterProjectsComboBox,
            self.ui.OKButton,
            self.ui.CancelButton,
        ]
        for wid in widgetsToMove:

            wid.setGeometry(wid.x(), wid.y()-pixels, wid.width(), wid.height())

    if not fromFLEx:

        # Hide a checkbox
        self.ui.selectAllChaptersCheckbox.setVisible(False)
        self.ui.scriptureTextsComboBox.setVisible(False)
        self.ui.scriptureTextsLabel.setVisible(False)

    # Initialize cluster projects (for import and from FLEx export)
    if (export == False or (export == True and fromFLEx == True)) and len(self.clusterProjects) > 0:

        ClusterUtils.initClusterProjects(self, self.clusterProjects, myMap.get('clusterProjects', []), self.ui.centralwidget)

        # Make ptx project selections in all visible combo boxes
        ptxProjList = myMap.get('ptxProjList', [])

        for i, ptxProj in enumerate(ptxProjList):

            if i < len(self.keyWidgetList):
                self.keyWidgetList[i].setCurrentText(ptxProj)
    else:
        # Hide cluster project widgets
        widgetsToHide = [
            self.ui.clusterProjectsLabel,
            self.ui.clusterProjectsComboBox,
        ]
        for wid in widgetsToHide:

            wid.setVisible(False)

    if fromFLEx:

        # Setup the checkable combo box for scripture text. ***Replace*** the one from the designer tool.
        geom = self.ui.scriptureTextsComboBox.geometry() # same as old control
        self.ui.scriptureTextsComboBox.hide()
        self.ui.scriptureTextsComboBox = CheckableComboBox(self.ui.centralwidget)
        geom.moveTo(geom.x(), self.ui.clusterProjectsComboBox.geometry().y()-30)  # move above cluster projects
        self.ui.scriptureTextsComboBox.setGeometry(geom)
        self.ui.scriptureTextsComboBox.setObjectName("scriptureTextsComboBox")
        self.ui.scriptureTextsComboBox.addItems([title for title in self.scriptureTitles if title])

        wid = self.ui.scriptureTextsLabel
        wid.setGeometry(wid.x(), self.ui.clusterProjectsComboBox.geometry().y()-30, wid.width(), wid.height())

        geom = self.ui.selectAllChaptersCheckbox.geometry()
        geom.moveTo(geom.x(), self.ui.clusterProjectsComboBox.geometry().y()-60)
        self.ui.selectAllChaptersCheckbox.setGeometry(geom)

        # Connect a custom signal to a function
        self.ui.scriptureTextsComboBox.itemCheckedStateChanged.connect(self.titlesSelectionChanged)

    # Now that the controls have been shown/hidden and positioned for this module, keep the user from resizing the window to where they would be clipped
    lockWindowSize(self)

def getParatextPath():

    # Get the Paratext path from the registry
    try:
        aKey = r"SOFTWARE\Wow6432Node\Paratext\8"
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        aKey = winreg.OpenKey(aReg, aKey)
        paratextPathTuple = winreg.QueryValueEx(aKey, "Settings_Directory")
        return paratextPathTuple[0]
    
    except Exception as e:
        return None
    
def doOKbuttonValidation(self, export=True, checkBookAbbrev=True, checkBookPath=True, fromFLEx=False, altParatextFolder=None):
    
    # Get values from the 'dialog' window
    projectAbbrev = self.ui.ptxProjAbbrevLineEdit.text()
    bookAbbrev = self.ui.bookAbbrevLineEdit.text().upper()
    fromChap = self.ui.fromChapterSpinBox.value()        
    toChap = self.ui.toChapterSpinBox.value()
    includeFootnotes = self.ui.footnotesCheckBox.isChecked()
    includeCrossRefs = self.ui.crossrefsCheckBox.isChecked()
    makeActive = self.ui.makeActiveTextCheckBox.isChecked()
    useFullBookName = self.ui.useFullBookNameForTitleCheckBox.isChecked()
    oneTextPerChapter = self.ui.oneTextPerChapterCheckBox.isChecked()
    includeIntro = self.ui.includeIntroCheckBox.isChecked()
    overwriteText = self.ui.overwriteExistingTextCheckBox.isChecked()
    numbersAsAnalysis = self.ui.numbersAsAnalysisCheckBox.isChecked()
    numberSeparators = self.ui.numberSeparatorLineEdit.text()

    ptxProjList = []

    if export == False or (export == True and fromFLEx == True):

        # Go through each visible Paratext combobox and get the value
        for myCombo in self.keyWidgetList:

            ptxProjList.append(myCombo.currentText())

    ## Validate some stuff
    
    # Check if the book is valid
    if checkBookAbbrev and bookAbbrev not in bookMap: 
        
        QMessageBox.warning(self, _translate("ChapterSelection", "Invalid Book Error"), _translate("ChapterSelection", "The book abbreviation: {bookAbbrev} is invalid.").format(bookAbbrev=bookAbbrev))
        return
    
    paratextPath = ""

    # Check if we need to use the alternate Paratext folder
    if not altParatextFolder:

        # Get the Paratext path
        paratextPath = getParatextPath()

        # If we get None, there was a registry problem
        if paratextPath is None:
            
            QMessageBox.warning(self, _translate("ChapterSelection", "Registry Error"), _translate("ChapterSelection", "Could not find the Paratext data folder in the registry."))
            return

        # Check if Paratext path exists
        if not os.path.exists(paratextPath): 

            QMessageBox.warning(self, _translate("ChapterSelection", "Not Found Error"), _translate("ChapterSelection", "Could not find the Paratext path: {paratextPath}.").format(paratextPath=Utils.shortenPathForDisplay(paratextPath)))
            return

    # If we have cluster projects, we don't check a couple of these things, error checking will have to be done for each project
    if export or self.ui.clusterProjectsComboBox.isHidden() or len(self.ui.clusterProjectsComboBox.currentData()) == 0:

        # Check if project path exists under Paratext (or the alternate folder)
        projPath = getProjectFolder(paratextPath, altParatextFolder, projectAbbrev)

        if not os.path.exists(projPath):
            
            QMessageBox.warning(self, _translate("ChapterSelection", "Not Found Error"), _translate("ChapterSelection", "Could not find that project at: {projPath}.").format(projPath=Utils.shortenPathForDisplay(projPath)))
            return

        # Importing needs the book file to be there already. Exporting doesn't: doExport() offers to create a book file the project doesn't have yet.
        if not export and checkBookPath and not findBookFile(projPath, bookAbbrev, projectAbbrev):

            QMessageBox.warning(self, _translate("ChapterSelection", "Not Found Error"), getBookNotFoundMessage(projPath, bookAbbrev, projectAbbrev))
            return

    if self.ui.clusterProjectsComboBox.isHidden():
        clustProjs = []
    else:
        clustProjs = self.ui.clusterProjectsComboBox.currentData()

    self.chapSel = ChapterSelection(export, self.otherProj, projectAbbrev, bookAbbrev, paratextPath, fromChap, toChap, includeFootnotes, includeCrossRefs, \
                                    makeActive, useFullBookName, overwriteText, clustProjs, ptxProjList, oneTextPerChapter, includeIntro, altParatextFolder, \
                                    numbersAsAnalysis, numberSeparators)
    
    # Save the settings to a file so the same settings can be shown next time
    f = open(self.settingsPath, 'w')
    
    dumpMap = self.chapSel.dump()
    json.dump(dumpMap, f, indent=4)
    
    f.close()
    
    self.retVal = True
    self.close()

def getFilteredSubdirectories(rootDir, excludeList):
    """
    Get a list of first-level subdirectories in rootDir, excluding those in excludeList or
    those that start with '_' or 'UserSettings'.
    """
    subdirectories = []
    
    if rootDir is None:

        return subdirectories
    
    for dirname in os.listdir(rootDir):

        dirpath = os.path.join(rootDir, dirname)

        if os.path.isdir(dirpath):

            if (dirname not in excludeList and not dirname.startswith('_') and not dirname.startswith('UserSettings')):
                
                subdirectories.append(dirname)

    return subdirectories

def getProjectFolder(paratextPath, altParatextFolder, projectAbbrev):

    # Without an alternate folder, the project is a subfolder of the Paratext data folder
    if not altParatextFolder:

        return os.path.join(paratextPath, projectAbbrev)

    # With an alternate folder, the project can have its own subfolder in it (e.g. a copy of a whole Paratext projects folder, which is what cluster projects usually need),
    # or its book files can sit directly in the alternate folder. Prefer the subfolder when there is one.
    subFolder = os.path.join(altParatextFolder, projectAbbrev)

    if projectAbbrev and os.path.isdir(subFolder):

        return subFolder

    return altParatextFolder

def getParatextBookNumStr(bookAbbrev):

    # Paratext numbers book files 01-39 for the Old Testament, then skips 40 so that Matthew is 41, and keeps counting up to 100 for XXG. From book 100 (FRT) on it switches to a letter
    # and a digit: A0-A9, B0-B9, C0-C3. So the number in 41MATABC.SFM is fixed by the book; it doesn't depend on how many books the project has.
    if bookAbbrev not in PARATEXT_BOOK_ORDER:

        return ''

    bookNum = PARATEXT_BOOK_ORDER.index(bookAbbrev) + 1

    if bookNum < 40:

        return f'{bookNum:02d}'

    if bookNum < 100:

        return str(bookNum + 1)

    return 'ABC'[(bookNum - 100) // 10] + str((bookNum - 100) % 10)

def getProjectSettingsRoot(projFolder):

    # The root element of the project's Settings.xml, or None when there is no Settings.xml to go by - which is normal for an alternate folder of loose book files
    settingsPath = os.path.join(projFolder, PARATEXT_SETTINGS_FILE)

    if not os.path.isfile(settingsPath):

        return None
    try:
        return ET.parse(settingsPath).getroot()

    except (ET.ParseError, OSError):

        return None

def getProjectNaming(projFolder):

    # A real Paratext project says how its book files are named in Settings.xml, e.g. <Naming PrePart="" PostPart="ABC.SFM" BookNameForm="41MAT" />. Returns (PrePart, BookNameForm, PostPart),
    # or None when there's nothing to go by.
    settingsRoot = getProjectSettingsRoot(projFolder)

    if settingsRoot is None:

        return None

    namingElem = settingsRoot.find('Naming')

    if namingElem is None:

        return None

    return (namingElem.get('PrePart', ''), namingElem.get('BookNameForm', '41MAT'), namingElem.get('PostPart', ''))

def makeBookFileName(naming, bookAbbrev):

    # BookNameForm is a sample of the book part of the name written for Matthew (41MAT, MAT, 41, ...), so put this book's number and abbreviation in place of Matthew's
    prePart, bookNameForm, postPart = naming
    bookPart = bookNameForm.replace('41', getParatextBookNumStr(bookAbbrev)).replace('MAT', bookAbbrev)

    return prePart + bookPart + postPart

def findBookFile(projFolder, bookAbbrev, projectAbbrev):

    # When the project has a Settings.xml, its naming gives the exact file name, whatever the extension
    naming = getProjectNaming(projFolder)

    if naming:

        bookPath = os.path.join(projFolder, makeBookFileName(naming, bookAbbrev))

        if os.path.isfile(bookPath):

            return bookPath

    # Otherwise look for <anything><book><project>.SFM, then .USFM. The wildcard takes the book number, which some projects leave out of their file names.
    for ext in ['.SFM', '.USFM']:

        fileList = glob.glob(os.path.join(projFolder, '*' + bookAbbrev + projectAbbrev + ext))

        if fileList:

            return fileList[0]

    return ''

def getNewBookFileName(projFolder, bookAbbrev, projectAbbrev):

    # Name a new book file the way the project names its book files, so that Paratext (and findBookFile()) will recognize it
    naming = getProjectNaming(projFolder)

    if naming:

        return makeBookFileName(naming, bookAbbrev)

    # Without a Settings.xml, follow the project's other book files in the folder, so that a folder of MATABC.SFM style files doesn't get a 41MATABC.SFM style file added to it.
    # With nothing to go by, use Paratext's default, e.g. 41MATABC.SFM.
    numStr = getParatextBookNumStr(bookAbbrev)
    ext = '.SFM'

    # The regex stubs type escape() as str or bytes; given a str it returns a str
    fileRE = r'^(?P<num>\d*|[A-C]\d)(?P<book>[A-Z0-9]{3})' + cast(str, re.escape(projectAbbrev)) + r'(?P<ext>\.u?sfm)$'

    if os.path.isdir(projFolder):

        for fileName in sorted(os.listdir(projFolder)):

            matchObj = re.match(fileRE, fileName, re.IGNORECASE)

            if matchObj and matchObj.group('book').upper() in bookMap:

                if not matchObj.group('num'):

                    numStr = ''

                ext = matchObj.group('ext')
                break

    return numStr + bookAbbrev + projectAbbrev + ext

def getBookNotFoundMessage(projFolder, bookAbbrev, projectAbbrev):

    # Name the file we wanted in plain terms - the book, the project, a file name of the right shape and the folder - rather than showing a wildcard search pattern
    return _translate("ChapterSelection", "Could not find the {bookName} book file for the {projAbbrev} project. It should be named like {fileName} and be in this folder: {folder}").format(
        bookName=bookMap.get(bookAbbrev, bookAbbrev), projAbbrev=projectAbbrev, fileName=getNewBookFileName(projFolder, bookAbbrev, projectAbbrev), folder=Utils.shortenPathForDisplay(projFolder))

def markBookPresent(projFolder, bookAbbrev):

    # Paratext keeps the list of books a project has in Settings.xml: <BooksPresent> is a string of 0s and 1s, one per book in PARATEXT_BOOK_ORDER. Flag the new book there so Paratext
    # shows it. The flag is changed as text rather than by parsing and rewriting the XML, so the rest of the file - its byte order mark and CRLF line endings included - stays exactly as it was.
    settingsPath = os.path.join(projFolder, PARATEXT_SETTINGS_FILE)

    if not os.path.isfile(settingsPath) or bookAbbrev not in PARATEXT_BOOK_ORDER:

        return

    with open(settingsPath, 'rb') as f:

        rawContents = f.read()

    hasBOM = rawContents.startswith(codecs.BOM_UTF8)
    contents = rawContents.decode('utf-8-sig')
    matchObj = re.search(r'<BooksPresent>([01]*)</BooksPresent>', contents)

    if not matchObj:

        return

    flags = matchObj.group(1).ljust(len(PARATEXT_BOOK_ORDER), '0')
    index = PARATEXT_BOOK_ORDER.index(bookAbbrev)
    flags = flags[:index] + '1' + flags[index+1:]
    contents = contents[:matchObj.start(1)] + flags + contents[matchObj.end(1):]

    with open(settingsPath, 'wb') as f:

        f.write((codecs.BOM_UTF8 if hasBOM else b'') + contents.encode('utf-8'))

def readVrsChapterCounts(vrsPath):

    # A Paratext .vrs file has one line per book giving each chapter's last verse, e.g. RUT 1:22 2:23 3:18 4:22, so the number of entries is the number of chapters. Some files (custom.vrs files
    # especially) end each book line with END, and a # starts a comment anywhere on a line. Verse mapping lines (GEN 31:55 = GEN 32:1) are skipped because the = and what follows it don't fit
    # the pattern, and excluded verse lines (-GEN 1:31) because they don't start with a book code. Returns {book: chapter count}, empty if the file can't be read. Don't change the dict that comes
    # back - it is the cached copy.
    # Parse each file only once per session. Versification files almost never change, so a file edited while FlexTools is running isn't noticed until FlexTools is restarted.
    # A file that is missing or can't be read is cached as empty too, so it isn't looked for again.
    cacheKey = os.path.normcase(os.path.abspath(vrsPath))

    if cacheKey in vrsChapterCountsCache:

        return vrsChapterCountsCache[cacheKey]

    counts = {}

    try:
        with open(vrsPath, encoding='utf-8-sig') as f:

            for line in f:

                matchObj = re.match(r'^([A-Z0-9]{3})((?:\s+\d+:\d+)+)(?:\s+END)?\s*$', line.split('#', 1)[0])

                if matchObj:

                    counts[matchObj.group(1)] = len(re.findall(r'\d+:', matchObj.group(2)))

    except (OSError, UnicodeDecodeError):

        counts = {}

    vrsChapterCountsCache[cacheKey] = counts

    return counts

def getBookChapterCount(projFolder, bookAbbrev):

    # How many chapters the book has in the project's versification, or 0 if that isn't known (e.g. FRT, GLO). Settings.xml's <Versification> number picks a standard versification, whose .vrs
    # file Paratext keeps in its projects folder - the project folder's parent in the standard layout. A custom.vrs in the project folder overrides the books it lists. When none of that can be
    # found (e.g. an alternate folder of loose book files), use English, Paratext's default versification.
    counts = None
    settingsRoot = getProjectSettingsRoot(projFolder)

    if settingsRoot is not None:

        versFile = VERSIFICATION_FILES.get(settingsRoot.findtext('Versification', '').strip())

        if versFile:

            for folder in [projFolder, os.path.dirname(os.path.normpath(projFolder))]:

                counts = readVrsChapterCounts(os.path.join(folder, versFile))

                if counts:

                    break

    if not counts:

        counts = ENGLISH_CHAPTER_COUNTS

    # custom.vrs wins for the books it lists. Look there first rather than merging it in, since counts may be a cached dict that mustn't be changed.
    customCounts = readVrsChapterCounts(os.path.join(projFolder, 'custom.vrs'))

    if bookAbbrev in customCounts:

        return customCounts[bookAbbrev]

    return counts.get(bookAbbrev, 0)

def createBookFile(bookPath, bookAbbrev, projFolder, exportChapters=None):

    # A new book starts with its \id line, which Paratext requires as the first line, followed by an empty placeholder (\c 1, \c 2, ...) for every chapter of the book, so the book has its
    # full shape in Paratext. doExport() then replaces the placeholders of the chapters being exported, and replaces the \id line if the text brings its own. If the text has chapters past the
    # versification's last chapter, placeholders go up to the highest of them so they still land in order.
    lastChapter = max([getBookChapterCount(projFolder, bookAbbrev)] + [int(ch) for ch in exportChapters or []])
    contents = '\\id ' + bookAbbrev + '\n' + ''.join(f'\\c {ch}\n' for ch in range(1, lastChapter + 1))

    with open(bookPath, 'w', encoding='utf-8') as f:

        f.write(contents)

    markBookPresent(projFolder, bookAbbrev)

def askToCreateBookFile(chapSelectObj, report, exportChapters):

    # Returns the path of the new book file, or '' if it wasn't created. exportChapters are the chapter numbers (as strings) the text holds.
    bookFolder = chapSelectObj.getBookFolder()
    projAbbrev = chapSelectObj.exportProjectAbbrev
    bookName = bookMap[chapSelectObj.bookAbbrev]

    # We create books, not projects, so the project folder has to be there. With cluster projects this is the first time a project's folder gets checked.
    if not os.path.isdir(bookFolder):

        report.Error(_translate("ChapterSelection", "Could not find that project at: {projPath}.").format(projPath=Utils.shortenPathForDisplay(bookFolder)))
        return ''

    bookPath = os.path.join(bookFolder, getNewBookFileName(bookFolder, chapSelectObj.bookAbbrev, projAbbrev))

    # Ask first, so a mistyped project or a wrong folder doesn't quietly leave a stray book file behind
    msgBox = QMessageBox()
    msgBox.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
    msgBox.setIcon(QMessageBox.Icon.Question)
    msgBox.setText(_translate("ChapterSelection", "The {projAbbrev} project does not have a {bookName} book file yet. Do you want to create one?\n\nIt will be created as: {bookPath}").format(projAbbrev=projAbbrev, bookName=bookName, bookPath=Utils.shortenPathForDisplay(bookPath)))
    msgBox.setWindowTitle(_translate("ChapterSelection", "Create book file"))
    msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    if msgBox.exec() == QMessageBox.StandardButton.No:

        report.Info(_translate("ChapterSelection", 'Export cancelled.'))
        return ''
    try:
        createBookFile(bookPath, chapSelectObj.bookAbbrev, bookFolder, exportChapters)

    except OSError as e:

        report.Error(_translate("ChapterSelection", "Could not create the book file: {bookPath}. {error}").format(bookPath=Utils.shortenPathForDisplay(bookPath), error=str(e)))
        return ''

    report.Info(_translate("ChapterSelection", "Created a new {bookName} book file in the {projAbbrev} project: {bookPath}. If the project is open in Paratext, close it and open it again to see the new book.").format(bookName=bookName, projAbbrev=projAbbrev, bookPath=Utils.shortenPathForDisplay(bookPath)))
    return bookPath

def getBookFileProjects(folder):

    # Work out the project abbreviations from the names of the book files sitting directly in the folder. Paratext names them <optional digits><book abbrev><project abbrev>.SFM,
    # e.g. 41MATABC.SFM, which is the same shape getBookPath() looks for. Only names whose three-letter book part is a real book count, so stray .sfm files don't make up projects.
    projSet = set()

    for fileName in os.listdir(folder):

        matchObj = re.match(r'^\d*(?P<book>[A-Z0-9]{3})(?P<proj>.+)\.u?sfm$', fileName, re.IGNORECASE)

        if matchObj and matchObj.group('book').upper() in bookMap:

            projSet.add(matchObj.group('proj'))

    return projSet

def getParatextProjects(altParatextFolder=None):

    excludeList = [
        'cms',
        'Temp Files',
    ]

    # Without an alternate folder, list the projects in the Paratext data folder
    if not altParatextFolder:

        return getFilteredSubdirectories(getParatextPath(), excludeList)

    if not os.path.isdir(altParatextFolder):

        return []

    # With an alternate folder, the projects are its subfolders that hold book files, plus any projects whose book files sit directly in it (see getProjectFolder())
    projSet = getBookFileProjects(altParatextFolder)

    for dirName in getFilteredSubdirectories(altParatextFolder, excludeList):

        if getBookFileProjects(os.path.join(altParatextFolder, dirName)):

            projSet.add(dirName)

    return sorted(projSet, key=str.lower)

def getScriptureText(report, textTitles):
    """
    Filters textTitles to match the criteria:
    - The book has to start with either an abbreviation or name that matches the dictionary bookMap.
    - The title will have a space and a two-digit chapter number and optionally a '-' and another two-digit chapter number.

    Parameters:
    - report: The report object for reporting.
    - textTitles: List of text titles to filter.

    Returns:
    - A list of filtered text titles.
    """
    filteredTitles = []

    for title in textTitles:

        match = bookChapterPattern.match(title)

        if match:

            book = match.group('book')
            chap1 = match.group('chap1')
            chap2 = match.group('chap2')
            normalizedBook = unicodedata.normalize("NFD", book)

            if book in bookMap or book in bookMap.values():

                filteredTitles.append(title)
                continue

            for val in bookMap.values():

                translatedStr = _translate("ChapterSelection", val)

                if normalizedBook == unicodedata.normalize("NFD", translatedStr):

                    filteredTitles.append(title)
                    break

    return sorted(filteredTitles)

def doExport(textContents, report, chapSelectObj, parent):
    
    # Find all the chapter #s
    myChapList = re.findall(r'\\c (\d+)', textContents, flags=re.RegexFlag.DOTALL)
    
    # Check that we have chapters in the syn. file
    if len(myChapList) < 1: 
        
        report.Error(_translate("ChapterSelection", "No chapters found in the text."))
        return None
    
    elif len(myChapList) > 1:
    
        chapStr = 'chapters'
        digitsStr = myChapList[0]+'-'+myChapList[-1]
    else:
        chapStr = 'chapter'
        digitsStr = myChapList[0]

    bookPath = chapSelectObj.getBookPath()
    newBook = False

    # If the project doesn't have this book yet, offer to create its book file. This applies whether the project is in the standard Paratext folder or the alternate one.
    if not bookPath:

        bookPath = askToCreateBookFile(chapSelectObj, report, myChapList)

        if not bookPath:

            return None

        newBook = True

    # Prompt the user to be sure they want to replace these chapters. A book that was just created has no chapters to replace.
    if not newBook and not chapSelectObj.dontShowWarning:

        # Create a QMessageBox instance
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setText(_translate("ChapterSelection", "Are you sure you want to overwrite {chapStr} {digitsStr} of {bookName} in the {projAbbrev} project?").format(chapStr=chapStr, digitsStr=digitsStr, bookName=bookMap[chapSelectObj.bookAbbrev], projAbbrev=chapSelectObj.exportProjectAbbrev))
        msgBox.setWindowTitle(_translate("ChapterSelection", "Overwrite chapters"))
        msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Add checkbox to the QMessageBox if we have multiple projects
        if len(chapSelectObj.clusterProjects) > 0:

            checkBox = QCheckBox(_translate("ChapterSelection", "Do not show this message again."))
            msgBox.setCheckBox(checkBox)
        
        # Display the message box and wait for user interaction
        ret = msgBox.exec()
        
        # Check if the checkbox was checked
        if len(chapSelectObj.clusterProjects) > 0 and checkBox.isChecked():

            chapSelectObj.dontShowWarning = True

        if ret == QMessageBox.StandardButton.No:

            report.Info(_translate("ChapterSelection", 'Export cancelled.'))
            return None

    # Create a backup of the paratext file (a new one holds nothing worth backing up)
    if not newBook:

        copyfile(bookPath, bookPath+'.bak')
    
    # Read the Paratext file
    with open(bookPath, encoding='utf-8') as f:

        bookContents = f.read()

    # If the incoming text carries an \id book-identifier line (import prepends it and keeps it in the Vernacular WS so it travels
    # through translation), use it to overwrite the \id line in the Paratext book. Both export modules funnel through here, so doing
    # this once covers them both. Its presence in textContents is the trigger - it's only there when chapter 1 was imported.
    synIdMatch = re.search(r'\\id .+', textContents)

    if synIdMatch:

        idLine = synIdMatch.group(0).rstrip()

        # Use a function replacement so the backslash in the \id line isn't interpreted as a group reference. Replace the book's
        # existing \id line, or prepend the line if the book somehow has none.
        if re.search(r'\\id .+', bookContents):

            bookContents = re.sub(r'\\id .+', lambda m: idLine, bookContents, count=1)
        else:
            bookContents = idLine + '\n' + bookContents

    # Find all the chapter #s
    ptxChapList = re.findall(r'\\c (\d+)', bookContents, flags=re.RegexFlag.DOTALL)
    
    # Split the synthesis contents into chapter chunks
    synContentsList = re.split(r'(\\c \d+)', textContents, flags=re.RegexFlag.DOTALL) # gives us [\c 1, \s ..., \c 2, \s ..., ...]
    haveIntro = False

    # Loop through each synthesis chapter and splice it into the paratext chapter contents
    for n in range(1, len(synContentsList), 2): # the zeroth one will be whatever is before the first \c, possibly the empty string
        
        # If we have chapter 1, and before chapter 1 is some intro stuff, add intro portion before chapter 1 marker and text
        if n == 1 and synContentsList[n] == '\\c 1' and re.search(r'\\ip', synContentsList[0]):

            haveIntro = True
            wholeChStr = synContentsList[0] + synContentsList[n] + synContentsList[n+1]

            # A new book's \id line is already at the top of the file (the text's own \id line replaced it above), so don't append a second one with the intro
            if newBook:

                wholeChStr = re.sub(r'\\id .+\n?', '', wholeChStr, count=1)
        else:
            wholeChStr = synContentsList[n] + synContentsList[n+1]
        
        # Check the corresponding chapter in the synthesis chapter list
        if myChapList[n//2] in ptxChapList:
            
            # If we have intro stuff to put in chapter 1, start the regex at \mt if it exists.
            if n == 1 and haveIntro:

                begRE = r'(\\mt.+\\c 1|\\c 1)'
            else:
                begRE = r'\\c ' + myChapList[n//2]
            
            # The (?!\d) keeps \c 1 from matching \c 10. The chapter's old contents may be empty - a chapter placeholder like \c 3 straight followed by \c 4 - so they are matched
            # with * rather than +. With + an empty chapter swallowed the next chapter marker, and an empty last chapter didn't match at all, so nothing was exported into it.
            replExtra = ''

            # See if this is the last paratext chapter: replace to the end of the book
            if myChapList[n//2] == ptxChapList[-1]:

                endRE = r'(?!\d).*'
            else:
                endRE = r'(?!\d).*?(?=\\c \d)' # non-greedy match up to (not including) the next chapter marker

                # The text's last chapter may not end with a line break; it needs one before the next chapter marker
                if not wholeChStr.endswith('\n'):

                    wholeChStr += '\n'
        else:
            found = False
            
            # Find the next chapter # in the list
            for i, ptxCh in enumerate(ptxChapList):
                
                if int(myChapList[n//2]) < int(ptxCh):
                    
                    found = True
                    break
            if found:

                # Insert ahead of the next higher chapter. The (?!\d) keeps \c 2 from also matching \c 20.
                begRE = r'\\c ' + ptxCh
                replExtra = '\\c ' + ptxCh
                endRE = r'(?!\d)'

                if not wholeChStr.endswith('\n'):

                    wholeChStr += '\n'
                
            # No next chapter found, just append
            else: 
                
                bookContents += wholeChStr
                continue
        
        # Escape each backslash
        wholeChStr = re.sub(r'\\', r'\\\\', wholeChStr + replExtra)    
        
        bookContents = re.sub(begRE + endRE, wholeChStr, bookContents, count=1, flags=re.RegexFlag.DOTALL)
        
    # Write the ptx file
    f = open(bookPath, 'w', encoding='utf-8')
    f.write(bookContents)
    
    # Close files
    f.close()

    # Report what got exported
    report.Info(_translate("ChapterSelection", "{chapStr} {digitsStr} of {bookName} exported to the {projAbbrev} project.").format(chapStr=chapStr.capitalize(), digitsStr=digitsStr, bookName=bookMap[chapSelectObj.bookAbbrev], projAbbrev=chapSelectObj.exportProjectAbbrev))
    return 1

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

Utils.loadTranslations(['ChapterSelection'], translators)

# Every book Paratext knows about, one row per book, in Paratext's canonical order. This is the one place book information lives; PARATEXT_BOOK_ORDER, bookMap and
# ENGLISH_CHAPTER_COUNTS below are derived from it, so a change to a book is made here and nowhere else. The columns are:
#   abbreviation - the three letter Paratext book code. A row's place in the table (counting from 1) is its Paratext book number, which the number at the front of a book file name is worked
#                  out from (see getParatextBookNumStr()), and it is also the order of the 0/1 flags in Settings.xml's <BooksPresent>, so rows must never be reordered, inserted or removed.
#   name         - the book name Paratext uses, translated into the UI language. The names are literal _translate() calls so the translation tools can find them, which is why this table
#                  comes after the translations are loaded. Names must be unique, since a FLEx text title can name its book by name instead of abbreviation.
#   chapters     - the number of chapters in the English versification (Paratext's default), from Paratext's eng.vrs, with ODA and PSS from FieldWorks' copy. 0 when unknown or
#                  when the book has no chapters (FRT, GLO, ...). Only used to make a new book's chapter placeholders when the project's own versification file can't be found.
BOOKS = [
    ('GEN', _translate("ChapterSelection", "Genesis"), 50),
    ('EXO', _translate("ChapterSelection", "Exodus"), 40),
    ('LEV', _translate("ChapterSelection", "Leviticus"), 27),
    ('NUM', _translate("ChapterSelection", "Numbers"), 36),
    ('DEU', _translate("ChapterSelection", "Deuteronomy"), 34),
    ('JOS', _translate("ChapterSelection", "Joshua"), 24),
    ('JDG', _translate("ChapterSelection", "Judges"), 21),
    ('RUT', _translate("ChapterSelection", "Ruth"), 4),
    ('1SA', _translate("ChapterSelection", "1 Samuel"), 31),
    ('2SA', _translate("ChapterSelection", "2 Samuel"), 24),
    ('1KI', _translate("ChapterSelection", "1 Kings"), 22),
    ('2KI', _translate("ChapterSelection", "2 Kings"), 25),
    ('1CH', _translate("ChapterSelection", "1 Chronicles"), 29),
    ('2CH', _translate("ChapterSelection", "2 Chronicles"), 36),
    ('EZR', _translate("ChapterSelection", "Ezra"), 10),
    ('NEH', _translate("ChapterSelection", "Nehemiah"), 13),
    ('EST', _translate("ChapterSelection", "Esther"), 10),
    ('JOB', _translate("ChapterSelection", "Job"), 42),
    ('PSA', _translate("ChapterSelection", "Psalms"), 150),
    ('PRO', _translate("ChapterSelection", "Proverbs"), 31),
    ('ECC', _translate("ChapterSelection", "Ecclesiastes"), 12),
    ('SNG', _translate("ChapterSelection", "Song of Solomon"), 8),
    ('ISA', _translate("ChapterSelection", "Isaiah"), 66),
    ('JER', _translate("ChapterSelection", "Jeremiah"), 52),
    ('LAM', _translate("ChapterSelection", "Lamentations"), 5),
    ('EZK', _translate("ChapterSelection", "Ezekiel"), 48),
    ('DAN', _translate("ChapterSelection", "Daniel"), 12),
    ('HOS', _translate("ChapterSelection", "Hosea"), 14),
    ('JOL', _translate("ChapterSelection", "Joel"), 3),
    ('AMO', _translate("ChapterSelection", "Amos"), 9),
    ('OBA', _translate("ChapterSelection", "Obadiah"), 1),
    ('JON', _translate("ChapterSelection", "Jonah"), 4),
    ('MIC', _translate("ChapterSelection", "Micah"), 7),
    ('NAM', _translate("ChapterSelection", "Nahum"), 3),
    ('HAB', _translate("ChapterSelection", "Habakkuk"), 3),
    ('ZEP', _translate("ChapterSelection", "Zephaniah"), 3),
    ('HAG', _translate("ChapterSelection", "Haggai"), 2),
    ('ZEC', _translate("ChapterSelection", "Zechariah"), 14),
    ('MAL', _translate("ChapterSelection", "Malachi"), 4),
    ('MAT', _translate("ChapterSelection", "Matthew"), 28),
    ('MRK', _translate("ChapterSelection", "Mark"), 16),
    ('LUK', _translate("ChapterSelection", "Luke"), 24),
    ('JHN', _translate("ChapterSelection", "John"), 21),
    ('ACT', _translate("ChapterSelection", "Acts"), 28),
    ('ROM', _translate("ChapterSelection", "Romans"), 16),
    ('1CO', _translate("ChapterSelection", "1 Corinthians"), 16),
    ('2CO', _translate("ChapterSelection", "2 Corinthians"), 13),
    ('GAL', _translate("ChapterSelection", "Galatians"), 6),
    ('EPH', _translate("ChapterSelection", "Ephesians"), 6),
    ('PHP', _translate("ChapterSelection", "Philippians"), 4),
    ('COL', _translate("ChapterSelection", "Colossians"), 4),
    ('1TH', _translate("ChapterSelection", "1 Thessalonians"), 5),
    ('2TH', _translate("ChapterSelection", "2 Thessalonians"), 3),
    ('1TI', _translate("ChapterSelection", "1 Timothy"), 6),
    ('2TI', _translate("ChapterSelection", "2 Timothy"), 4),
    ('TIT', _translate("ChapterSelection", "Titus"), 3),
    ('PHM', _translate("ChapterSelection", "Philemon"), 1),
    ('HEB', _translate("ChapterSelection", "Hebrews"), 13),
    ('JAS', _translate("ChapterSelection", "James"), 5),
    ('1PE', _translate("ChapterSelection", "1 Peter"), 5),
    ('2PE', _translate("ChapterSelection", "2 Peter"), 3),
    ('1JN', _translate("ChapterSelection", "1 John"), 5),
    ('2JN', _translate("ChapterSelection", "2 John"), 1),
    ('3JN', _translate("ChapterSelection", "3 John"), 1),
    ('JUD', _translate("ChapterSelection", "Jude"), 1),
    ('REV', _translate("ChapterSelection", "Revelation"), 22),
    ('TOB', _translate("ChapterSelection", "Tobit"), 14),
    ('JDT', _translate("ChapterSelection", "Judith"), 16),
    ('ESG', _translate("ChapterSelection", "Esther Greek"), 10),
    ('WIS', _translate("ChapterSelection", "Wisdom of Solomon"), 19),
    ('SIR', _translate("ChapterSelection", "Sirach"), 51),
    ('BAR', _translate("ChapterSelection", "Baruch"), 6),
    ('LJE', _translate("ChapterSelection", "Letter of Jeremiah"), 1),
    ('S3Y', _translate("ChapterSelection", "Song of the 3 Young Men"), 1),
    ('SUS', _translate("ChapterSelection", "Susanna"), 1),
    ('BEL', _translate("ChapterSelection", "Bel and the Dragon"), 1),
    ('1MA', _translate("ChapterSelection", "1 Maccabees"), 16),
    ('2MA', _translate("ChapterSelection", "2 Maccabees"), 15),
    ('3MA', _translate("ChapterSelection", "3 Maccabees"), 7),
    ('4MA', _translate("ChapterSelection", "4 Maccabees"), 18),
    ('1ES', _translate("ChapterSelection", "1 Esdras (Greek)"), 9),
    ('2ES', _translate("ChapterSelection", "2 Esdras (Latin)"), 16),
    ('MAN', _translate("ChapterSelection", "Prayer of Manasseh"), 1),
    ('PS2', _translate("ChapterSelection", "Psalm 151"), 1),
    ('ODA', _translate("ChapterSelection", "Odae/Odes"), 14),
    ('PSS', _translate("ChapterSelection", "Psalms of Solomon"), 18),
    ('JSA', _translate("ChapterSelection", "Joshua (Greek, Codex Alexandrinus)"), 24),
    ('JDB', _translate("ChapterSelection", "Judges (Greek, Codex Vaticanus)"), 21),
    ('TBS', _translate("ChapterSelection", "Tobit (Greek, Codex Sinaiticus)"), 14),
    ('SST', _translate("ChapterSelection", "Susanna (Greek, Theodotion)"), 1),
    ('DNT', _translate("ChapterSelection", "Daniel (Greek, Theodotion)"), 12),
    ('BLT', _translate("ChapterSelection", "Bel and the Dragon (Greek, Theodotion)"), 1),
    ('XXA', _translate("ChapterSelection", "Extra A"), 0),
    ('XXB', _translate("ChapterSelection", "Extra B"), 0),
    ('XXC', _translate("ChapterSelection", "Extra C"), 0),
    ('XXD', _translate("ChapterSelection", "Extra D"), 0),
    ('XXE', _translate("ChapterSelection", "Extra E"), 0),
    ('XXF', _translate("ChapterSelection", "Extra F"), 0),
    ('XXG', _translate("ChapterSelection", "Extra G"), 0),
    ('FRT', _translate("ChapterSelection", "Front matter"), 0),
    ('BAK', _translate("ChapterSelection", "Back matter"), 0),
    ('OTH', _translate("ChapterSelection", "Other matter"), 0),
    ('3ES', _translate("ChapterSelection", "3 Esdras"), 0),
    ('EZA', _translate("ChapterSelection", "Ezra Apocalypse"), 0),
    ('5EZ', _translate("ChapterSelection", "5 Ezra"), 0),
    ('6EZ', _translate("ChapterSelection", "6 Ezra"), 0),
    ('INT', _translate("ChapterSelection", "Introduction"), 0),
    ('CNC', _translate("ChapterSelection", "Concordance"), 0),
    ('GLO', _translate("ChapterSelection", "Glossary"), 0),
    ('TDX', _translate("ChapterSelection", "Topical index"), 0),
    ('NDX', _translate("ChapterSelection", "Names index"), 0),
    ('DAG', _translate("ChapterSelection", "Daniel Greek"), 14),
    ('PS3', _translate("ChapterSelection", "Psalms 152-155"), 0),
    ('2BA', _translate("ChapterSelection", "2 Baruch (Apocalypse)"), 0),
    ('LBA', _translate("ChapterSelection", "Letter of Baruch"), 0),
    ('JUB', _translate("ChapterSelection", "Jubilees"), 0),
    ('ENO', _translate("ChapterSelection", "Enoch"), 0),
    ('1MQ', _translate("ChapterSelection", "1 Meqabyan/Mekabis"), 0),
    ('2MQ', _translate("ChapterSelection", "2 Meqabyan"), 0),
    ('3MQ', _translate("ChapterSelection", "3 Meqabyan"), 0),
    ('REP', _translate("ChapterSelection", "Reproof"), 0),
    ('4BA', _translate("ChapterSelection", "4 Baruch"), 0),
    ('LAO', _translate("ChapterSelection", "Letter to the Laodiceans"), 1),
]

PARATEXT_BOOK_ORDER = [abbrev for abbrev, name, chapters in BOOKS]
bookMap = {abbrev: name for abbrev, name, chapters in BOOKS}
ENGLISH_CHAPTER_COUNTS = {abbrev: chapters for abbrev, name, chapters in BOOKS if chapters}
