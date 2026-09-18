#
#   GenerateParses
#
#   Version 3.17.1 - 9/12/26 - Ron Lockwood
#    Count only stems that can generate output against the stem limit. Added the code description block.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.2 - 6/30/26 - Ron Lockwood
#    Fixes #1397. Shortened file paths shown in user messages with Utils.shortenPathForDisplay().
#
#   Version 3.16.1 - 6/26/26 - Ron Lockwood
#    Prevent the module from starting in one-project mode.
#
#   Version 3.16 - 4/30/26 - Ron Lockwood
#    Bump to version 3.16.
#
#   Version 3.15.1 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15 - 2/6/26 - Ron Lockwood
#    Bumped to 3.15.
#
#   Version 3.14.1 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14 - 5/18/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   20 Aug 2024 rl v3.11  Bumped to 3.11
#   18 Jan 2023 rl v3.10  Bumped to 3.10
#   17 Aug 2023 rl v3.9.4 More changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#   12 Aug 2023 rl v3.9.3 Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#   17 Jul 2023 bb v3.9.2 Test morphType by GUID, not by name in Primary Ana WS
#   21 Jun 2023 rl v3.9.1 Use the target DB instead of the source DB (passed in from FlexTools)
#   20 Jun 2023 rl v3.9   Cleaned up imports, modified description slightly, bumped version #
#   16 Jun 2023 bb v2.0   Integrate with FLExTrans: Use FLExTrans
#                         SettingsGUI.py and Utils.py.  Change name
#                         to GenerateParses.py
#   02 Aug 2022 bb v1.17  Only use active templates. Read settings from config file.
#   26 Jun 2022 bb v1.12  Change to FLExLookup-MakeAnaFile.py.
#                         Output directly to .ana format, not transferred text.
#   26 Jun 2022 bb v1.11  Finish updating for FlexTools 2.1 (fix error in v1.10)
#                         Includes counter to allow processing a small number of
#                         stems, during initial setup and debugging.
#   22 Jun 2022 bb v1.10  Update for FlexTools 2.1 (new flexlibs for FW 9.1.8+)
#
#   28 May 2022 bb        Change filename and primary function:
#                         Original was for testing writing systems and didn't
#                         use any Synthesis module.
#
#   Original:       03 Oct 2016
#   Ron Lockwood
#   SIL International
#
#   OVERVIEW (AI generated, then edited)
#
#   This module walks a target FLEx project's lexicon and writes out every inflected word form that the project's affix templates are able to produce. It is the input generator for
#   the Synthesis Test workflow: you run it to get an exhaustive list of parses, feed that list to a Synthesizer module, and then compare what the synthesizer actually produced
#   against what the lexicon and the templates said should have been possible. That comparison is how a target project's morphology gets shaken out before the project is used for
#   real translation.
#
#   Generation is driven entirely by the inflectional affix templates, not by any text data. For each stem the module finds the templates attached to the stem's category, and for
#   each template it takes the cross product of every affix sitting in each of that template's slots (plus the empty string for a slot that is optional). Clitics are then appended
#   to each form that comes out. The result is combinatorial, so a project of any size produces a very large file - which is why the Synthesis Test settings exist to narrow a run
#   down to one category, one citation form, or a random sample of N stems.
#
#   THE TWO OUTPUT FILES
#
#   Every generated word is written twice, to two files that have to stay line-for-line parallel. The Transfer Results File gets the Apertium form (^lexeme1.1<pos><tag>...$), which
#   is what a Synthesizer module consumes. The Parses Output File gets the human readable form, built from glosses rather than lexeme forms, so that a person can read down the list
#   and see what each line was meant to mean. The parses file starts with a blank line because the synthesized file it will be compared against also starts with one; remove that
#   line and every comparison afterward is off by one.
#
#   CATEGORY HIERARCHIES
#
#   FLEx grammatical categories form a tree - 'Transitive Verb' can sit under 'Verb' - and a template hung on a parent category applies to all of its descendants. get_cat2focus
#   builds cat2focus, which maps each category to itself plus every category beneath it, so that a template found on 'Verb' also gets registered for the child categories. Note that
#   categories are keyed throughout by abbreviation *plus* GUID (abbr2str), never by abbreviation alone, because FLEx is perfectly happy to let two different categories share an
#   abbreviation.
#
#   THE STEM LIMIT
#
#   The SynthesisTestLimitStemCount setting is meant to mean 'generate from this many stems', and honoring it takes two steps that are easy to get backwards. standardSpellList
#   collects every stem entry in the lexicon regardless of its category, so before that list is shuffled and sliced down to the limit it first has to be filtered to the stems that
#   will actually produce output - and a stem produces output only if its own category is a focus category or if a derivational affix moves it into one. Slicing the unfiltered list
#   instead fills the sample with a mix of usable and unusable stems, and the run then quietly generates from fewer stems than were asked for.
#
#   UNHANDLED SCENARIOS
#
#   Variant forms that have no senses of their own are skipped rather than resolved back to the entry they vary. An entry with more than one grammatical category is reduced to the
#   category of its first sense, and an affix with more than one MSA is likewise reduced. Clitics are generated but it is not settled which form of a clitic belongs in a parse, and
#   they do not currently show up in the surface forms. Root glosses get a hard-coded '1.1' homograph and sense number instead of the real ones from FLEx.
#
#   CODE STRUCTURE
#
#   name2str and abbr2str build the GUID-qualified keys described above. Slot and Template are dataclasses read out of FLEx by their fromDB methods; Template.generate yields the
#   prefix/suffix tag combinations for one template, and Template.inflect wraps those around a stem and appends clitics, producing the (Apertium form, gloss form) pairs that get
#   written out. get_cat2focus builds the category hierarchy map along with the set of focus categories, and get_templ_list collects the Active templates for those categories.
#   stemYieldsOutput answers whether a single stem's category can reach a focus category, and is what filters the stem list before the limit is applied. get_stems then walks the
#   filtered list and yields one entry per (stem, output category) pair, derived categories included. MainFunction ties it all together: read the settings, loop through the lexicon
#   once to fill standardSpellList (stems), cat2CliticList (clitics), derivAffixList (derivational affixes) and slot2AffixList (inflectional affixes by slot), apply the stem limit,
#   and then for every stem run every template belonging to its category and write both output files.
#

from dataclasses import dataclass
import itertools
from collections import defaultdict
import random
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

from SIL.LCModel import ( # type: ignore
    IMoStemMsa,
    IMoInflAffMsa,
    IMoDerivAffMsa,
    )
from flextoolslib import * # type: ignore

import Mixpanel
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'GenerateParses'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("GenerateParses", "Generate All Parses"),
        FTM_Version    : "3.17.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("GenerateParses", "Creates all possible parses from a FLEx project, in Apertium format."),
        FTM_Help       : "",
        FTM_Description:_translate("GenerateParses", 
"""This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn't generate based on derivation information in the project and it doesn't yet handle
clitics or variants.)
In FLExTrans > Settings, under Synthesis Test settings, it is possible to limit output to
a single POS or Citation Form, or to a specified number of stems (stems will be chosen
randomly). This module also outputs a human readable version of the parses (with glosses of roots
and affixes) to the Parses Output File specified in the settings.""")}

#app.quit()
#del app

#----------------------------------------------------------------

# Configurables:
## (Should this be set in the config file now?)

# Morphnames to process
STEM_MORPH_NAMES = ['stem','bound stem','root','bound root','phrase']


#----------------------------------------------------------------

logger = logging.getLogger(__name__)

def name2str(obj):
    return f'{Utils.as_string(obj.Name)}:{obj.Guid.ToString()}'

def abbr2str(cat):
    return Utils.as_string(cat.Abbreviation) + cat.Guid.ToString()

@dataclass
class Slot:
    name: str
    required: bool

    @staticmethod
    def fromDB(slot):
        return Slot(name2str(slot), not slot.Optional)

@dataclass
class Template:
    name: str
    prefixes: list[Slot]
    suffixes: list[Slot]
    valid: bool = True
    slot_tags = None

    @staticmethod
    def fromDB(templ):
        prefixes = [Slot.fromDB(s) for s in reversed(templ.PrefixSlotsRS)]
        suffixes = [Slot.fromDB(s) for s in templ.SuffixSlotsRS]
        return Template(name2str(templ), prefixes, suffixes)

    def get_slot_tags(self, morphemes):
        if self.slot_tags is None:
            self.slot_tags = []
            for slot in (self.prefixes + self.suffixes):
                tags = list(morphemes[slot.name])
                if not slot.required:
                    tags.append('')
                if not tags:
                    logger.info(_translate("GenerateParses", "No tags found for slot {slotName} of template {templateName}. Skipping.").format(slotName=slot.name, templateName=self.name))
                    self.valid = False
                    return
                self.slot_tags.append(sorted(tags))

    def generate(self, morphemes):
        self.get_slot_tags(morphemes)
        if not self.valid:
            return

        split = len(self.prefixes)
        for tag_list in itertools.product(*self.slot_tags):
            yield ''.join(tag_list[:split]), ''.join(tag_list[split:])

    def inflect(self, morphemes, aStem, gStem, clitics):
        for prefixes, suffixes in self.generate(morphemes):
            aForm = aStem + prefixes + suffixes
            gForm = prefixes + gStem + suffixes
            yield aForm, gForm
            for isProclitic, tag in clitics:
                t = f'<{tag}>'
                if isProclitic:
                    yield aForm + t, t + gForm
                else:
                    yield aForm + t, gForm + t

def get_cat2focus(DB, focusPOS):
    keep = set()

    children = {}
    for cat in DB.lp.AllPartsOfSpeech:
        label = abbr2str(cat)
        children[label] = set()
        for subcat in cat.SubPossibilitiesOS:
            children[label].add(abbr2str(subcat))
        if Utils.as_string(cat.Abbreviation) in focusPOS:
            keep.add(label)

    cat2focus = defaultdict(set)
    for pos in children:
        cat2focus[pos].add(pos)
        todo = list(children[pos])
        while todo:
            c = todo.pop()
            cat2focus[pos].add(c)
            todo += list(children[c])

    return cat2focus, keep

# Build a map from categories to templates and maps from templates to slots
def get_templ_list(myDB, cat2focus, report):
    logger.info('Processing templates')

    cat2templ = defaultdict(list)
    templates = {}

    for gcat in myDB.lp.AllPartsOfSpeech:

        catAbbrev = Utils.as_string(gcat.Abbreviation)
        catLabel = abbr2str(gcat)
        cats = cat2focus[catLabel]
        if len(cats) == 0:
            # This POS is not an ancestor of any of the ones we care about,
            # so skip it.
            continue

        templList = []
        # Loop through all templates for this category
        for templ in gcat.AffixTemplatesOS:

            # If it is marked as not Active in FLEx, then don't add it to the list
            # that will be processed later
            if templ.Disabled == True:
                #report.Info("Not adding template "+templName+' for Category '+catAbbrev)
                logger.info(_translate("GenerateParses", "  Not adding Inactive template {templateName} for Category {categoryAbbrev}").format(templateName=Utils.as_string(templ.Name), categoryAbbrev=catAbbrev))
                continue

            templObj = Template.fromDB(templ)
            logger.info(_translate("GenerateParses", "  Adding template {templateName} for Category {categoryAbbrev}").format(templateName=templObj.name, categoryAbbrev=catAbbrev))
            for c in cats:
                cat2templ[c].append(templObj.name)
            templates[templObj.name] = templObj

    return cat2templ, templates

# Will this stem produce any output? It will if its own category is one of the focus categories, or if a derivational affix moves it into one. Only stems that answer yes ever
# reach the output files, so only those should be counted against the stem limit.
def stemYieldsOutput(posKey, derivAffixList, outputCats):

    if posKey in outputCats:

        return True

    for _, toPos, _ in derivAffixList[posKey]:

        if toPos in outputCats:

            return True

    return False

def get_stems(standardSpellList, derivAffixList, maxStems, outputCats):
    random.shuffle(standardSpellList)
    stems = 0

    for lemma, gloss, pos_tag, pos_key in standardSpellList:
        yield_any = False

        aStem = f'{lemma}<{pos_tag}>'
        gStem = f'{gloss}<{pos_tag}>'

        if pos_key in outputCats:
            yield (aStem, gStem, pos_key)
            yield_any = True

        for tag, toPos, isPrefix in derivAffixList[pos_key]:
            if toPos in outputCats:
                yield (aStem,
                       (tag + gStem) if isPrefix else (gStem + tag),
                       toPos)
                yield_any = True

        if yield_any:
            stems += 1
            if stems >= maxStems:
                break

def MainFunction(DB, report, modifyAllowed):

    slot2AffixList = defaultdict(list)
    cat2CliticList = defaultdict(set)
    derivAffixList = defaultdict(list)
    standardSpellList = []

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    twoProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False)
    if twoProjectMode == 'n':
        report.Error(_translate("GenerateParses", "This module only works in Two Project mode."))
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Open the target project
    DB = Utils.openTargetProject(configMap, report)

    # initialize a logfile, for debugging
    targetLOG = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LOG_FILE, report)
    if not targetLOG:
        return

    logFile = Utils.build_path_default_to_temp(targetLOG)
    try:
        logger.addHandler(logging.FileHandler(logFile, mode='w', encoding='utf-8'))
        report.Info(_translate("GenerateParses", "Logging to {logFile}").format(logFile=Utils.shortenPathForDisplay(logFile)))
    except:
        report.Error(_translate("GenerateParses", "There was a problem creating the log file: {logFile}.").format(logFile=Utils.shortenPathForDisplay(logFile)))

    ## Generate for only a specified POS  (This needs work)
    focusPOS = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_POS, report)
    if focusPOS == "":
        report.Error(_translate("GenerateParses", '  No focus POS. Please select at least one POS with a template.'))
        return
    else:
        # last POS is likely empty
        if focusPOS[-1] == '':
            focusPOS.pop()
        report.Info(_translate("GenerateParses", "  Only collecting templates for these POS: {focusPOS}").format(focusPOS=str(focusPOS)))

    cat2focus, outputCats = get_cat2focus(DB, focusPOS)

    report.Info(_translate("GenerateParses", "Collecting templates from FLEx project..."))

    # Get maps related to templates
    # cat2templ will come back with a list of the Active templates that were added
    # It will only add Templates for focusPOS, if set
    cat2templ, templates = get_templ_list(DB, cat2focus, report)

    ## To make it easier to check the output when starting up, only take a specified number of stem entries
    maxStems = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_STEM_COUNT, report)
    if maxStems == "":
        maxStems = DB.LexiconNumberOfEntries()
        report.Info(_translate("GenerateParses", '  Not limiting number of stems'))
    else:
        maxStems = int(maxStems)
        report.Info(_translate("GenerateParses", "  Only generating on the first {maxStems} stems").format(maxStems=str(maxStems)))

    ## Generate for only a specified Lexeme Form  (This needs work)
    focusLex = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_LEXEME, report)

    logger.info(_translate("GenerateParses", 'Processing entries'))
    report.ProgressStart(DB.LexiconNumberOfEntries())

    # Loop through all the entries
    for entryCount,e in enumerate(DB.LexiconAllEntries()):

        report.ProgressUpdate(entryCount)

        morphGuidStr = e.LexemeFormOA.MorphTypeRA.Guid.ToString()
        morphType = Utils.morphTypeMap[morphGuidStr]

        # Stem-types (not affixes, clitics)
        if e.LexemeFormOA and \
           e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           morphType in STEM_MORPH_NAMES:

            # This number can be adjusted in the config file, if you want to stop after a greater number of stems
            ## (There could be better logic here!!  Maybe a while loop would be better.)

            ##
            # Get the Citation Form of this entry (or Lexeme Form, if Citation Form is empty)
            lex = DB.LexiconGetCitationForm(e) or DB.LexiconGetLexemeForm(e)
            if not lex:
                continue

            ## This is where we would limit to a specific Citation Form
            if focusLex != "":
                if lex != focusLex:
                    continue
                else:
                    report.Info(_translate("GenerateParses", "  Only generating on stem [{lex}]\n").format(lex=lex))

            # Add Homograph.SenseNum to use it as an underlying form for STAMP
            ## (Really need to get the actual HM and SN from FLEx, and use all of them.)
            lex += '1.1'

            # if there are no senses, skip to the next (because this must be a variant)
            # The "continue" makes it skip; the "GetEntryWithSense(e) tries to find the appropriate
            # sense for this variant.  But it wasn't working right.
            if e.SensesOS.Count < 1:
                logger.info(_translate("GenerateParses", "  Skipping Variant with {count} Senses: {lex}").format(count=str(e.SensesOS.Count), lex=lex))
                continue

            # Also store the Gloss of the root (first sense only, so far)
            thisGloss = ''

            # reset variable
            catAndGuid = ''
            # BB: Set the POS to UNK, so it will have some value even if the sense doesn't.
            # (Had to add this after the upgrade to FlexTools 2.1.)
            pos = 'UNK'
            # Loop through senses (once). Entries without senses get skipped
            for s in e.SensesOS:
                if not thisGloss:
                    thisGloss = DB.LexiconGetSenseGloss(s) or 'NoGloss'

                # Make sure we have a valid analysis object
                if not s.MorphoSyntaxAnalysisRA:
                    continue

                # Skip non-stems
                if s.MorphoSyntaxAnalysisRA.ClassName != 'MoStemMsa':
                    continue

                if msa_pos := IMoStemMsa(s.MorphoSyntaxAnalysisRA).PartOfSpeechRA:
                    catAndGuid = abbr2str(msa_pos)
                    pos = Utils.as_string(msa_pos.Abbreviation) or 'UNK'
                    # Just get the grammatical info. for the 1st sense and stop
                    # BB: The word may have multiple senses, but we really only
                    # care about the POS of the template we generated from.
                    break

            if lex and catAndGuid:
                logger.info(_translate("GenerateParses", "  Adding [{thisGloss}]{lex}<{pos}> to roots list").format(thisGloss=thisGloss, lex=lex, pos=pos))
                standardSpellList.append((lex, thisGloss, pos, catAndGuid))
                # If one of these words is missing a gloss, report it to the Messages window
                if thisGloss == 'NoGloss':
                    report.Info(_translate("GenerateParses", "Using NoGloss as the gloss for {lex}.").format(lex=lex))

        else: # non-stems

            # Get the lexeme form (object)
            lex = DB.LexiconGetLexemeForm(e)

            if lex is None or len(lex) == 0:
                continue

            # BB: Do we need to get the Citation form for clitics, and/or wrap them also?
            if morphType in ['proclitic','enclitic']:

                if e.MorphoSyntaxAnalysesOC:

                    msa = e.MorphoSyntaxAnalysesOC.ToArray()[0]

                    if msa.ClassName == 'MoStemMsa':

                        msa = IMoStemMsa(msa)
                    else:
                        logger.info(_translate("GenerateParses", "Skipping deriv MSA for {lex}").format(lex=lex))
                        continue

                    for s in e.SensesOS:
                        lex = '<'+Utils.underscores(DB.LexiconGetSenseGloss(s))+'>'
                        break

                    # Get categories that this clitic can attach to
                    for gcat in msa.FromPartsOfSpeechRC:

                        cat2CliticList[abbr2str(gcat)].add(
                            (morphType == 'proclitic', lex))

            # Get Glosses for affixes.  (just the first gloss for now)
            elif morphType in ['suffix', 'prefix']:

                # BB: Store the Lexeme Form of this affix, just for debugging purposes
                # Remembering it because we are about to adjust lex
                lexForm = lex

                # Find the first Sense, get the Gloss, and wrap in < > for the parses output
                for s in e.SensesOS:
                    lex = '<'+Utils.underscores(DB.LexiconGetSenseGloss(s))+'>'
                    break

                for sense in e.SensesOS:
                    if sense.MorphoSyntaxAnalysisRA.ClassName != 'MoDerivAffMsa':
                        continue
                    msa = IMoDerivAffMsa(sense.MorphoSyntaxAnalysisRA)
                    if not msa.FromPartOfSpeechRA or not msa.ToPartOfSpeechRA:
                        continue
                    fPos = abbr2str(msa.FromPartOfSpeechRA)
                    tPos = abbr2str(msa.ToPartOfSpeechRA)
                    for mappedPos in cat2focus[tPos]:
                        derivAffixList[fPos].append((lex, mappedPos, morphType == 'prefix'))

                if e.MorphoSyntaxAnalysesOC:

                    # Get the slots associated with this affix
                    for msa in e.MorphoSyntaxAnalysesOC.ToArray(): # might be multiple msas
                        # And if the same slot is in more than one category, it will have a different GUID
                        # in each one.  So it may look like one affix is being added to the same slot
                        # multiple times.
                        # Which kind of MSA is this?
                        #report.Info(str(type(msa)))

                        if msa.ClassName == 'MoInflAffMsa':

                            msa = IMoInflAffMsa(msa)
                        else:
                            continue

                        # First get the POS for this MSA, just for debug output
                        if msa.PartOfSpeechRA == None:
                            report.Error(_translate("GenerateParses", "MSA missing POS in {lexForm} {lex}").format(lexForm=lexForm, lex=lex))
                            continue
                        if not Utils.as_string(msa.PartOfSpeechRA.Abbreviation):
                            report.Error(_translate("GenerateParses", "POS msaPOS missing Abbreviation label"))
                        for slot in msa.Slots:
                            name = name2str(slot)
                            slot2AffixList[name].append(lex)
                            # BB: For debugging, log each time we add an affix to a slot
                            logger.info(_translate("GenerateParses", "      Adding affix {lexForm} {lex} to slot [{slotName}]").format(lexForm=lexForm, lex=lex, slotName=Utils.as_string(slot.Name)))

            # Report if it's a morph type we don't handle
            else:
                logger.info(_translate("GenerateParses", "Morph type {morphType} ignored.").format(morphType=morphType))

    # standardSpellList holds every stem entry in the lexicon, including ones in categories we aren't generating for. Those have to be dropped before the sample is taken, otherwise
    # they use up slots in it and the run generates from fewer stems than the user asked for - ask for five and get three because two of the five drawn were the wrong category.
    standardSpellList = [stemInfo for stemInfo in standardSpellList if stemYieldsOutput(stemInfo[3], derivAffixList, outputCats)]

    if len(standardSpellList) > maxStems:

        random.shuffle(standardSpellList)
        standardSpellList = standardSpellList[:maxStems]
        standardSpellList.sort()

    report.Info(_translate("GenerateParses", "Finished collecting templates. Now generating words."))

    ## Open output files, before constructing parses

    ## First get the filenames from the config file
    transferResultsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    targetUF = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_PARSES_OUTPUT_FILE, report)

    if not targetUF:
        return

    # Open one file to write results directly in Apertium format, to be converted into whichever format
    # is needed for the chosen Synthesizer module
    aperFile = Utils.build_path_default_to_temp(transferResultsFile)
    try:
        f_aper = open(aperFile, 'w', encoding='utf-8')
    except IOError as e:
        report.Error(_translate("GenerateParses", "There was a problem creating the Apertium file: {aperFile}.").format(aperFile=Utils.shortenPathForDisplay(aperFile)))

    # Open another file where the results can be formatted as an end product itself (showing the parses
    # in human readable form)
    outFile = Utils.build_path_default_to_temp(targetUF)
    try:
        f_out = open(outFile, 'w', encoding='utf-8')
    except IOError as e:
        report.Error(_translate("GenerateParses", "There was a problem creating the words file: {outFile}.").format(outFile=Utils.shortenPathForDisplay(outFile)))
    # We need a blank line at the beginning of the file, to match the synthesized file.
    f_out.write('\n')

    cat2clitic = {}
    for cat, focusCats in cat2focus.items():
        clitics = set()
        for f in focusCats:
            clitics.update(cat2CliticList[f])
        cat2clitic[cat] = sorted(clitics)

    for key in derivAffixList:
        derivAffixList[key].sort()

    # Process each word and add affixes and clitics
    # Then output the full set of inflections for each word
    wrdCount = 0
    for aStem, gStem, pos_key in get_stems(standardSpellList, derivAffixList, maxStems, outputCats):
        for templName in cat2templ[pos_key]:
            templ = templates[templName]

            for aForm, gForm in templ.inflect(slot2AffixList, aStem, gStem,
                                              cat2clitic[pos_key]):
                wrdCount += 1
                f_aper.write(f'^{aForm}$\n')
                f_out.write(gForm + '\n')

    ## Output final counts to the log file.
    logger.info('\n\n' + _translate("GenerateParses", "{wrdcnt} words generated.").format(wrdcnt=str(wrdCount)) + '\n')

    # report.Info('Creation complete to the file: '+sigFile+'.')
    report.Info(_translate("GenerateParses", "Creation complete to the file: {outFile}.").format(outFile=Utils.shortenPathForDisplay(outFile)))
    report.Info(_translate("GenerateParses", "{wrdCount} words generated.").format(wrdCount=str(wrdCount)))

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
