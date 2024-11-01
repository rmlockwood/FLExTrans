#
#   GenerateParses
#
#   Create a list of all word parses that can be generated from a FLEx project with
#   lexicon, grammatical categories, and templates for some of the categories.
#
#   Finds inflectional affixes (and clitics) that could go on each kind of word
#   and generates all possible parses (morphological representations).
#   The resulting file can be used with a Synthesis module to produce inflected words.
#
#   Unhandled scenarios: variant forms without senses (skipped),
#   multiple grammatical categories, multiple MSAs for affixes,
#   clitics (which form in parses? don't currently appear in surface forms), putting
#   the correct homograph/sense number on root glosses
#
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

import re
import copy
from dataclasses import dataclass
import itertools
from collections import defaultdict
import random
import logging

from SIL.LCModel import (
    IMoStemMsa,
    IMoInflAffMsa,
    IMoDerivAffMsa,
    )
from flextoolslib import *

import Utils
import ReadConfig

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Generate All Parses",
        FTM_Version    : "3.12",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Creates all possible parses from a FLEx project, in Apertium format.",
        FTM_Help       :"",
        FTM_Description:
"""
This module creates an Apertium file (that can be converted for input to a Synthesizer process) with
all the parses that can be generated from the target FLEx project, based on its inflectional templates.
(It doesn't generate based on derivation information in the project and it doesn't yet handle
clitics or variants.)
In FLExTrans > Settings, under Synthesis Test settings, it is possible to limit output to
a single POS or Citation Form, or to a specified number of stems (stems will be chosen
randomly). This module also outputs a human readable version of the parses (with glosses of roots
and affixes) to the Parses Output File specified in the settings.
""" }

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
                    logger.info(f'No tags found for slot {slot.name} of template {self.name}. Skipping.')
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
        if pos in keep:
            cat2focus[pos].add(pos)
        todo = list(children[pos])
        while todo:
            c = todo.pop()
            if c in keep:
                cat2focus[pos].add(c)
            todo += list(children[c])

    return cat2focus

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
                logger.info("  Not adding Inactive template "+Utils.as_string(templ.Name)+' for Category '+catAbbrev)
                continue

            templObj = Template.fromDB(templ)
            logger.info("  Adding template "+templObj.name+' for Category '+catAbbrev)
            for c in cats:
                cat2templ[c].append(templObj.name)
            templates[templObj.name] = templObj

    return cat2templ, templates

def MainFunction(DB, report, modifyAllowed):
    slot2AffixList = defaultdict(list)
    cat2CliticList = defaultdict(set)
    derivAffixList = defaultdict(list)
    standardSpellList = []

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
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
        report.Info('Logging to '+logFile)
    except:
        report.Error('There was a problem creating the log file: '+logFile+'.')

    ## Generate for only a specified POS  (This needs work)
    focusPOS = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_POS, report)
    if focusPOS == "":
        report.Error('  No focus POS. Please select at least one POS with a template.')
        return
    else:
        # last POS is likely empty
        if focusPOS[-1] == '':
            focusPOS.pop()
        report.Info('  Only collecting templates for these POS: '+str(focusPOS))

    cat2focus = get_cat2focus(DB, focusPOS)

    report.Info("Collecting templates from FLEx project...")

    # Get maps related to templates
    # cat2templ will come back with a list of the Active templates that were added
    # It will only add Templates for focusPOS, if set
    cat2templ, templates = get_templ_list(DB, cat2focus, report)

    ## To make it easier to check the output when starting up, only take a specified number of stem entries
    maxStems = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_STEM_COUNT, report)
    if maxStems == "":
        maxStems = DB.LexiconNumberOfEntries()
        report.Info('  Not limiting number of stems')
    else:
        maxStems = int(maxStems)
        report.Info('  Only generating on the first '+str(maxStems)+' stems')

    ## Generate for only a specified Lexeme Form  (This needs work)
    focusLex = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_LEXEME, report)

    logger.info('Processing entries')
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
                    report.Info('  Only generating on stem ['+lex+']\n')

            # Add Homograph.SenseNum to use it as an underlying form for STAMP
            ## (Really need to get the actual HM and SN from FLEx, and use all of them.)
            lex += '1.1'

            # if there are no senses, skip to the next (because this must be a variant)
            # The "continue" makes it skip; the "GetEntryWithSense(e) tries to find the appropriate
            # sense for this variant.  But it wasn't working right.
            if e.SensesOS.Count < 1:
                logger.info('  Skipping Variant with '+str(e.SensesOS.Count)+' Senses: '+lex)
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

            # Only add words of the desired POS to the list to be inflected
            if pos not in focusPOS:
                continue

            if lex and catAndGuid:
                logger.info(f'  Adding [{thisGloss}]{lex}<{pos}> to roots list')
                standardSpellList.append((lex, thisGloss, pos, catAndGuid))
                # If one of these words is missing a gloss, report it to the Messages window
                if thisGloss == 'NoGloss':
                    report.Info('  Using NoGloss as the gloss for ' + lex +'\n')

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
                        logger.info("Skipping deriv MSA for "+lex)
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
                            report.Error('MSA missing POS in '+lexForm+' '+lex)
                            continue
                        if not Utils.as_string(msa.PartOfSpeechRA.Abbreviation):
                            report.Error('POS msaPOS missing Abbreviation label')
                        for slot in msa.Slots:
                            name = name2str(slot)
                            slot2AffixList[name].append(lex)
                            # BB: For debugging, log each time we add an affix to a slot
                            logger.info('\n      Adding affix '+lexForm+' '+lex+' to slot ['+Utils.as_string(slot.Name)+']')

            # Report if it's a morph type we don't handle
            else:
                logger.info('\nMorph type ' + morphType + ' ignored')

    if len(standardSpellList) > maxStems:
        random.shuffle(standardSpellList)
        standardSpellList = standardSpellList[:maxStems]
        standardSpellList.sort()

    report.Info('Finished collecting templates.  Now generating words.')
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
        report.Error('There was a problem creating the Apertium file: '+aperFile+'.')

    # Open another file where the results can be formatted as an end product itself (showing the parses
    # in human readable form)
    outFile = Utils.build_path_default_to_temp(targetUF)
    try:
        f_out = open(outFile, 'w', encoding='utf-8')
    except IOError as e:
        report.Error('There was a problem creating the words file: '+outFile+'.')
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
    for lemma, gloss, pos_tag, pos_key in standardSpellList:

        aStem = f'{lemma}<{pos_tag}>'
        gStem = f'{gloss}<{pos_tag}>'

        for templName in cat2templ[pos_key]:
            templ = templates[templName]

            for aForm, gForm in templ.inflect(slot2AffixList, aStem, gStem,
                                              cat2clitic[pos_key]):
                wrdCount += 1
                f_aper.write(f'^{aForm}$\n')
                f_out.write(gForm + '\n')

        for tag, toPos, isPrefix in derivAffixList[pos_key]:
            aStemDeriv = aStem + tag
            gStemDeriv = (tag + gStem) if isPrefix else (gStem + tag)

            for templName in cat2templ[toPos]:
                templ = templates[templName]

                for aForm, gForm in templ.inflect(slot2AffixList, aStemDeriv,
                                                  gStemDeriv, cat2clitic[toPos]):
                    wrdCount += 1
                    f_apr.write(f'^{aForm}$\n')
                    f_out.write(gForm + '\n')

    ## Output final counts to the log file.
    logger.info('\n\n'+str(wrdCount)+' words generated.'+'\n')

#    report.Info('Creation complete to the file: '+sigFile+'.')
    report.Info('Creation complete to the file: '+outFile+'.')
    report.Info(str(wrdCount)+' words generated.')

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
