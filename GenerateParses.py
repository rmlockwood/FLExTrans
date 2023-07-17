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
import itertools

from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString         
from flextoolslib import *

import Utils
import ReadConfig

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Generate All Parses",
        FTM_Version    : "3.9",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Creates all possible parses from a FLEx project, in Apertium format.",
        FTM_Help       :"",
        FTM_Description:  
u"""
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

def verifySlots(slot2AffixList, slot2IsPrefix):
    badSlots = []
    for slotName in slot2IsPrefix:
        if slotName not in slot2AffixList:
            badSlots.append(slotName)
    return badSlots

def catalog_subcats(myDB):
    cat2subCat = {}
    for gcat in myDB.lp.AllPartsOfSpeech:
        # Build the category name
        catAndGuid= ITsString(gcat.Abbreviation.BestAnalysisAlternative).Text + gcat.Guid.ToString()
        
        subCatList = []
        # Loop through all templates for this category
        for subcat in gcat.SubPossibilitiesOS:
            # Build the template name
            subCatAndGuid= ITsString(subcat.Abbreviation.BestAnalysisAlternative).Text + subcat.Guid.ToString()
            
            subCatList.append(subCatAndGuid)
        
        if len(subCatList) > 0:
            cat2subCat[catAndGuid] = subCatList
        
    return cat2subCat
                
def push_templates_down(posList, templs2Assign, cat2Templ, cat2subCat):
    # Loop through categories
    for cat in posList:
        
        # If we already have templates for this category, add to the list
        if cat in cat2Templ:
            templList = cat2Templ[cat]
            
            # Add the new templates if they are not already present
            for t2A in templs2Assign:
                if t2A not in templList:
                    templList.append(t2A)
        else:
            # Initialize it
            if len(templs2Assign) > 0:
                cat2Templ[cat] = templs2Assign
            templList = templs2Assign
    
        newT2A = templList
        
        # if this category has sub-categories call this function recursively
        if cat in cat2subCat and len(newT2A) > 0:
            push_templates_down(cat2subCat[cat], newT2A, cat2Templ, cat2subCat)
            
def push_clitics_down(posList, clitics2Assign, cat2CliticList, cat2subCat):
    # Loop through categories
    for cat in posList:
        
        # If we already have clitics for this category, add to the list
        if cat in cat2CliticList:
            cliticList = cat2CliticList[cat]
            
            # Add the new clitics if they are not already present
            for c2A in clitics2Assign:
                if c2A not in cliticList:
                    cliticList.append(c2A)
        else:
            # Initialize it
            if len(clitics2Assign) > 0:
                cat2CliticList[cat] = clitics2Assign
            cliticList = clitics2Assign
    
        newT2A = cliticList
        
        # if this category has sub-categories call this function recursively
        if cat in cat2subCat and len(newT2A) > 0:
            push_templates_down(cat2subCat[cat], newT2A, cat2CliticList, cat2subCat)
            
MAX_CLITICS = 2
# recursive word creation
def add_clitics(wordPair, cliticPairList, masterList):

    masterList.append(wordPair)
    #print wordPair[0].encode('utf-8')
    for i in range(1,MAX_CLITICS+1):
        for iterList in itertools.permutations(cliticPairList,i):
            newWord = wordPair
            for cliticPair in iterList:
                if cliticPair[0]: # True if it's a proclitic
                    newWord = cliticPair[1]+newWord
                else:
                    newWord = newWord+cliticPair[1]
            masterList.append(newWord)

# Add all possible affixes for the given slots
def add_affixes(stemList, slotList):

    # if we don't have any slots we don't do anything
    if len(slotList) > 0:
        # remove the first slot
        curSlot = slotList.pop(0)
        
        # make spare copies of the slots and stems
        newSlotList = copy.deepcopy(slotList)
        newStemList = copy.deepcopy(stemList)
        
        # now that we have a copy of the stems, set it back to no stems
        # this is because we keep building on stems without keeping the first set
        # E.g. for stem+slot1+slot2, we want all combos where slot1 and slot2 are present
        # process_slots takes care of slots missing in other iterations
        # if slot1=a,b and slot2=x,y we would expect stemax,stemay,stembx,stemby to result
        stemList = []
        
        # Loop through all stems in the list
        for stem in newStemList: # stem is a tuple of two stems
            # Loop through all affixes for the current slot we are adding
            (prefix, mySlot) = curSlot
            for afx in mySlot: # afx is the Gloss of an affix, wrapped in < >
                # Put prefixes before the stem+pos and suffixes after
                if prefix:
                    stemList.append(afx+stem)
                else:
                    stemList.append(stem+afx)
        
        # Recursively call this routine to get the affixes for the next slot
        # The list of slots is one less because we removed the first one
        stemList = add_affixes(stemList, newSlotList)
        
    # return the inflections we just built. We can't pass by reference because we set stemList to [] above
    return stemList

# Find all possible slot combinations
# infSlots and masterList start out as empty
# infSlots being empty means no slots applied (just the stem) which is valid. The first one in the masterList will be this empty list.
# infSlots are the ones that we have done so far and grows each time.
def process_slots(infSlots, slotList, masterList): 
    # The first append, this saves a combination to the master list.
    masterList.append(infSlots)         
    
    # Always make a copy of the slot list, so that the callers list coming in doesn't get destroyed by a pop()           
    newSlotList = copy.deepcopy(slotList) 
    
    # Loop through all our slots              
    # The deeper in recursion we are, the fewer slots are in this list because they keep getting popped()     
    for slot in slotList: 
        newInflSlots = copy.deepcopy(infSlots)
        
        # add the current slot combination we are processing to the list
        newInflSlots.append(slot)

        # remove the first slot in the list for the next recursion
        newSlotList.pop(0) 
        
        process_slots(newInflSlots, newSlotList, masterList)

# Build a map from categories to templates and maps from templates to slots
def get_templ_list(myDB, cat2Templ, templ2Slots, slot2IsPrefix, catList, focusPOS, f_log, report):
    f_log.write('\nProcessing templates')

    for gcat in myDB.lp.AllPartsOfSpeech:
    
        # I could screen for POS right here. I could choose to only add
        # templates to the templList if they match the designated POS.
        # But I need to not circumvent the part that pushes templates down to
        # child categories, if the focus POS inherits its templates from a parent.
        
        # Build the category name
        catAbbrev = ITsString(gcat.Abbreviation.BestAnalysisAlternative).Text
        if catAbbrev == "***":
            catFullName = ITsString(gcat.Name.BestAnalysisAlternative).Text
            report.Error('Error: category '+catFullName+' missing Abbreviation')
            # Even if this Error occurs, we can go on, because *** will get added to the GUID
        
        catAndGuid=catAbbrev + gcat.Guid.ToString()

        # I don't think this is doing anything right here.
        if focusPOS != "":
            if catAbbrev not in focusPOS:
                continue
        
        # Add to the list of categories
        # This list is used in the Main function to push templates down.  What else?
        catList.append(catAndGuid)
        
        templList = []
        # Loop through all templates for this category
        for templ in gcat.AffixTemplatesOS:
            # Build the template name
            templName = ITsString(templ.Name.BestAnalysisAlternative).Text
            templAndGuid = templName + templ.Guid.ToString()

            # If it is marked as not Active in FLEx, then don't add it to the list
            # that will be processed later
            if templ.Disabled == True:
                #report.Info("Not adding template "+templName+' for Category '+catAbbrev)
                f_log.write("\n  Not adding Inactive template "+templName+' for Category '+catAbbrev)
                continue
            else:
                #report.Info("Adding template "+templName+' for Category '+catAbbrev)
                f_log.write("\n  Adding template "+templName+' for Category '+catAbbrev)
                templList.append(templAndGuid)
            
            slotList = []
            oblSlotList = []
            # Get the prefix slots for this template
            for slot in templ.PrefixSlotsRS:
                # Build slot name
                slotName = catAbbrev + ":" + ITsString(slot.Name.BestAnalysisAlternative).Text  + ":" + slot.Guid.ToString()
                
                # For prefixes put things in reverse order. i.e. don't append from the end of the list
                # like for suffixes, prepend to the beginning of the list
                slotList.insert(0,slotName) 
                f_log.write("\n      Adding prefix slot "+slotName+" to template "+templName)
                
                slot2IsPrefix[slotName] = True # prefix=True
                
                # Add to the obligatory slot list if needed
                if not slot.Optional:
                    oblSlotList.append(slotName)
                    
            # Get the suffix slots for this template
            for slot in templ.SuffixSlotsRS:
                # Build slot name
                slotName = catAbbrev + ":" + ITsString(slot.Name.BestAnalysisAlternative).Text  + ":" + slot.Guid.ToString()
                #f_log.write("\n      Checking slot "+slotName+" in template "+templName)
                
                slotList.append(slotName)
                f_log.write("\n      Adding suffix slot "+slotName+" to template "+templName)
                
                slot2IsPrefix[slotName] = False # prefix=True

                # Add to the obligatory slot list
                if not slot.Optional and slotName not in oblSlotList:
                    oblSlotList.append(slotName)
            
            # Add to the map
            templ2Slots[templAndGuid] = (slotList, oblSlotList)
        
        # Add to the map    
        if len(templList) > 0:
            cat2Templ[catAndGuid] = templList
            f_log.write('\n    Added cat '+catAndGuid+ 'to templList '+str(templList))

    f_log.write('\n')
            
# Add all possible inflectional affixes using all applicable templates
def create_words_from_templates(wordPair, templList, tmpl2Slots, slot2AffixList, slot2IsPrefix):

    # List of all the inflected forms for this stem (collect to be the return value of this function)
    wordParadigmList = []
    
    # Loop through each template in the templList which is for one category
    for templAndGuid in templList:
        # Get the slots and obligatory slots for this template
        (slotList, oblSlotList) = tmpl2Slots[templAndGuid]
        
        slotCombos = [] 
        prelimSlotCombos = []
        # Create all slot combinations
        process_slots([], slotList, prelimSlotCombos)
        
        oblSlotSet = set(oblSlotList)
        # Create slot combinations where obligatory slots are represented
        for prelimCombo in prelimSlotCombos:
            prelimComboSet = set(prelimCombo)
            
            # All the obligatory slots have to be in the current slot combination
            if oblSlotSet.issubset(prelimComboSet):
                slotCombos.append(prelimCombo)
                
        # Loop through each combination
        for combo in slotCombos:
            affixList = []
            
            # Loop through each slot in the slot combination
            for slotAndGuid in combo:
                # Add to the list of  affixes. This creates a list of lists of affixes. The outer list corresponds to each slot in the combo. I.e. a list of affixes for each slot.
                affixList.append((slot2IsPrefix[slotAndGuid], slot2AffixList[slotAndGuid]))
            
            # Cycle through all affixes in the slots, attach to the word portion of the word/cat pair that was passed in   
            comboWords = add_affixes([wordPair[0]], affixList)
            
            # Add to a list that will be further formatted before printing as intermediate files for the user
            wordParadigmList.extend(comboWords)
    
    return wordParadigmList
            
def MainFunction(DB, report, modifyAllowed):
    cat2Templ = {}
    templ2Slots = {}
    slot2AffixList = {}
    cat2CliticList = {}
    slot2IsPrefix = {}
    standardSpellList = []
    catList = []
    wrdCount = 0
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Open the target project
    DB = Utils.openTargetProject(configMap, report)

    # initialize a logfile, for debugging
    targetLOG = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LOG_FILE, report)
    if not targetLOG:
        return 

    logFile = Utils.build_path_default_to_temp(targetLOG)
    try:
        f_log = open(logFile, 'w', encoding='utf-8')
    except IOError as e:
        report.Error('There was a problem creating the log file: '+logFile+'.')

    ## Generate for only a specified POS  (This needs work)
    focusPOS = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_POS, report)
    if focusPOS == "":
        report.Info('  No focus POS. Applying to all POS with templates.')
    else:
        # last POS is likely empty
        if focusPOS[-1] == '':
            focusPOS.pop()
        report.Info('  Only collecting templates for these POS: '+str(focusPOS))
        
    report.Info("Collecting templates from FLEx project...")
    report.ProgressStart(DB.LexiconNumberOfEntries())
    
    # Get maps related to templates
    # cat2Templ will come back with a list of the Active templates that were added
    # It will only add Templates for focusPOS, if set
    get_templ_list(DB, cat2Templ, templ2Slots, slot2IsPrefix, catList, focusPOS, f_log, report)
    
    # Get a map of categories to subcategories
    cat2Subcats = catalog_subcats(DB)
    
    # Copy templates down to any child categories
    push_templates_down(catList, [], cat2Templ, cat2Subcats)
    
    
    ## To make it easier to check the output when starting up, only take a specified number of stem entries
    maxStems = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_STEM_COUNT, report)
    if maxStems == "":
        # Set a high value if nothing was defined in the settings
        maxStems = 9999
        report.Info('  Not limiting number of stems')
    else:
        maxStems = int(maxStems)
        report.Info('  Only generating on the first '+str(maxStems)+' stems')
    stemCount = 0
    
    ## Generate for only a specified Lexeme Form  (This needs work)
    focusLex = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LIMIT_LEXEME, report)

    f_log.write('\nProcessing entries')

    # Loop through all the entries
    for entryCount,e in enumerate(DB.LexiconAllEntries()):
    
        report.ProgressUpdate(entryCount)
        
        morphType = ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text
        
        # Stem-types (not affixes, clitics)
        if e.LexemeFormOA and \
           e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           morphType in STEM_MORPH_NAMES:
        
            # This number can be adjusted in the config file, if you want to stop after a greater number of stems
            ## (There could be better logic here!!  Maybe a while loop would be better.)
            if stemCount >= maxStems:
                # After the first n stems (of the focus POS type), don't process stem type entries, 
                # but continue the loop, looking for more entries
                # (We want to traverse all the affixes.)
               continue
            
            ## 
            # Get the Citation Form of this entry (or Lexeme Form, if Citation Form is empty)
            if DB.LexiconGetCitationForm(e):
                lex = DB.LexiconGetCitationForm(e)
            else:
                lex = DB.LexiconGetLexemeForm(e)
                
            ## This is where we would limit to a specific Citation Form
            if focusLex != "":
                if lex != focusLex:
                    continue
                else:
                    report.Info('  Only generating on stem ['+lex+']\n')

            # Also store the Gloss of the root (first sense only, so far)
            for mySense in e.SensesOS:
                thisGloss = DB.LexiconGetSenseGloss(mySense)
                break
            if thisGloss == '':
                thisGloss = 'NoGloss'
                ## Don't need to report this for every word this applies to; only the ones we're using, later
                #report.Info('  Using '+thisGloss+' for '+lex+'\n')
                
            # Add Homograph.SenseNum to use it as an underlying form for STAMP
            ## (Really need to get the actual HM and SN from FLEx, and use all of them.)
            # Also attach the Gloss on the front, so we can use it later for a different output.
            if lex is None or len(lex) == 0:
                continue
            else:
                # Format for parses output file
                lex = '['+thisGloss+']'+lex+'1.1'
            # Reset
            thisGloss = ""

            # if there are no senses, skip to the next (because this must be a variant)
            # The "continue" makes it skip; the "GetEntryWithSense(e) tries to find the appropriate
            # sense for this variant.  But it wasn't working right.
            if e.SensesOS.Count < 1:
                f_log.write('\n  Skipping Variant with '+str(e.SensesOS.Count)+' Senses: '+lex)
                continue
#                e = GetEntryWithSense(e)
                
            # reset variable
            catAndGuid = ''
            # Loop through senses (once). Entries without senses get skipped
            for mySense in e.SensesOS:
                # BB: Set the POS to UNK, so it will have some value even if the sense doesn't.
                # (Had to add this after the upgrade to FlexTools 2.1.)
                pos = "UNK"
                
                # Make sure we have a valid analysis object
                if mySense.MorphoSyntaxAnalysisRA:
                
                    # Get the POS abbreviation for the current sense, assuming we have a stem
                    if mySense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                        
                        if mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA: 
                            # get grammatical category ID           
                            catAndGuid = ITsString(mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                                  Abbreviation.BestAnalysisAlternative).Text + \
                                                  mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.Guid.ToString()
                            # get grammatical category for underlying form
                            pos = ITsString(mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                                  Abbreviation.BestAnalysisAlternative).Text
                            
                # Add Category to Lexeme Form, to use it as an underlying form for STAMP
                ## (If none specified, call it UNK)
                if pos is None or len(pos) == 0:
                    pos = 'UNK'
                # Format for parses file
                lex = lex+'<'+pos+'>'

                # Just get the grammatical info. for the 1st sense and stop
                # BB: The word may have multiple senses, but we really only
                # care about the POS of the template we generated from.
                break

            # Only add words of the desired POS to the list to be inflected
            if focusPOS != "" and pos in focusPOS:
                if lex and catAndGuid:
                    stemCount+=1
                    f_log.write('\n  Adding '+lex+' to roots list')
                    standardSpellList.append((lex,catAndGuid))
                    # If one of these words is missing a gloss, report it to the Messages window
                    m = re.match( '^\[(NoGloss)\](.+)1.1', lex)
                    if m:
                        temp_gloss = m.group(1)
                        temp_citform = m.group(2)
                        report.Info('  Using ' + temp_gloss + ' as the gloss for ' + temp_citform +'\n')
                        temp_gloss = temp_citform = ''
                        
                 
            #else:
            #    f_log.write('\nSkipping '+lex+' '+catAndGuid)
                                                  
        else: # non-stems
                 
            # Get the lexeme form (object) 
            lex = DB.LexiconGetLexemeForm(e)
            
            if lex is None or len(lex) == 0:
                continue
    
            # BB: Do we need to get the Citation form for clitics, and/or wrap them also?
            if morphType in ['proclitic','enclitic']:  
                  
                if e.MorphoSyntaxAnalysesOC: 
                    
                    # Get categories that this clitic can attach to
                    for gcat in e.MorphoSyntaxAnalysesOC.ToArray()[0].FromPartsOfSpeechRC:
                        # Build the cat name
                        catAndGuid = ITsString(gcat.Abbreviation.BestAnalysisAlternative).Text + gcat.Guid.ToString()
                        
                        # If the category is not yet in the map, initialize it
                        if catAndGuid not in cat2CliticList:
                            cat2CliticList[catAndGuid] = []
                            
                        existingCliticList = cat2CliticList[catAndGuid]
                        
                        if morphType == 'proclitic':
                            existingCliticList.append((True, lex)) # Use True for proclitics
                        else: # enclitic
                            existingCliticList.append((False, lex))
                
            # Get Glosses for affixes.  (just the first gloss for now)
            elif morphType in ['suffix', 'prefix']:   
                  
                # BB: Store the Lexeme Form of this affix, just for debugging purposes
                # Remembering it because we are about to adjust lex
                lexForm = lex
                
                # Find the first Sense, get the Gloss, and wrap in < > for the parses output
                if e.SensesOS.Count > 0:
                    #f_log.write('\n      Sense count: '+lexForm+'\t'+str(e.SensesOS.Count))
                    #f_log.write('\n       Affix: '+lexForm)
                    for mySense in e.SensesOS:
                        lex = DB.LexiconGetSenseGloss(mySense)
                        # Change dot to underscore, in affix glosses
                        lex = re.sub(r'\.', '_', lex)
                        ## Also wrap affix glosses in { } to prevent possible conflicts with root glosses
                        # Not doing this now.  Instead, check the FLEx project for duplicate glosses.
                        # TODO: Do these scripts already check for that?
                        #lex = '{'+lex+'}'
#                      #  report.Info("lex = "+lex)
                        # Format for parses file
                        lex = '<'+lex+'>'
                        #f_log.write('  Gloss: '+lex)
                        # We only need to do the first sense.  When it looks for all the MSAs of this entry, it will find them for all senses.
                        break

                if e.MorphoSyntaxAnalysesOC:
                    
                    # Get the slots associated with this affix
                    for msa in e.MorphoSyntaxAnalysesOC.ToArray(): # might be multiple msas
                        # And if the same slot is in more than one category, it will have a different GUID
                        # in each one.  So it may look like one affix is being added to the same slot 
                        # multiple times.
                        # Which kind of MSA is this?
                        #report.Info(str(type(msa)))
                        
                        if str(type(msa)) == "<class 'SIL.LCModel.DomainImpl.MoDerivAffMsa'>":
                            #report.Info("Skipping deriv MSA "+str(type(msa)))
                            f_log.write("Skipping deriv MSA for "+lexForm+'  '+lex)
                            continue
                        #else:
                            #report.Info("Processing infl MSA "+str(type(msa)))

                        # First get the POS for this MSA, just for debug output
                        if msa.PartOfSpeechRA == None:
                            report.Error('MSA missing POS in '+lexForm+' '+lex)
                            continue
                        msaPOS = ITsString(msa.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
                        if msaPOS == "":
                            msaPOS = ITsString(msa.PartOfSpeechRA.Name.BestAnalysisAlternative).Text
                            report.Error('POS msaPOS missing Abbreviation label')
                        for slot in msa.Slots: 
                            # Build the slot name
                            slotFriendlyName = ITsString(slot.Name.BestAnalysisAlternative).Text
                            slotName = msaPOS + ":" + slotFriendlyName + ":" + slot.Guid.ToString()
                         
                            # Add affix glosses to the map showing which affixes are in this slot
                            # If the slotname is not in the map yet, initialize it
                            if slotName not in slot2AffixList:
                                slot2AffixList[slotName] = [lex]
                                # BB: For debugging, log each time we add an affix to a slot
                                f_log.write('\n      Adding affix '+lexForm+' '+lex+' to ['+msaPOS+'] slot ['+slotFriendlyName+']')
                            
                            else:   
                                # Otherwise find the list of affixes associated with this slot and add to it.
                                existingAffixList = slot2AffixList[slotName]
                                existingAffixList.append(lex)

            # Report if it's a morph type we don't handle
            else:
                f_log.write('\nMorph type ' + morphType + ' ignored')
            
    # Verify that we have affixes in each slot. If not give an error
    badSlots = verifySlots(slot2AffixList, slot2IsPrefix)
    for bSlot in badSlots:
        report.Error('Found slot with no affixes: ' + bSlot)
        f_log.write('\nFound slot with no affixes: ' + bSlot)
    
    if len(badSlots) > 0:
        return    
    
    report.Info('Finished collecting templates.  Now generating words.')
    ## Open output files, before constructing parses

    ## First get the filenames from the config file
    transferResultsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    targetANA = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report)
    targetUF = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_PARSES_OUTPUT_FILE, report)
    targetSIG = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_SIGMORPHON_OUTPUT_FILE, report)

    if not (targetANA and targetUF): # if targetSIG is missing, don't exit.
        return 
    
    # Open one file to write results directly in Apertium format, to be converted into whichever format 
    # is needed for the chosen Synthesizer module
    aperFile = Utils.build_path_default_to_temp(transferResultsFile)
    try:
        f_aper = open(aperFile, 'w', encoding='utf-8')
    except IOError as e:
        report.Error('There was a problem creating the Apertium file: '+aperFile+'.')
        
    # Open another file to write results directly in .ana format, for input to STAMP
    anaFile = Utils.build_path_default_to_temp(targetANA)
    try:
        f_ana = open(anaFile, 'w', encoding='utf-8')
    except IOError as e:
        report.Error('There was a problem creating the ana file: '+anaFile+'.')
        
    # Open another file where the results can be formatted as an end product itself (showing the parses
    # in human readable form)
    outFile = Utils.build_path_default_to_temp(targetUF)
    try:
        f_out = open(outFile, 'w', encoding='utf-8')
    except IOError as e:
        report.Error('There was a problem creating the words file: '+outFile+'.')
    # We need a blank line at the beginning of the file, to match the synthesized file.
    f_out.write('\n')
        
#    # Open another file for SIGMORPHON style results
#    sigFile = Utils.build_path_default_to_temp(targetSIG)
#    try:
#        f_sig = open(sigFile, 'w', encoding='utf-8')
#    except IOError as e:
#        report.Error('There was a problem creating the SIG file: '+sigFile+'.')
#    # We need a blank line at the beginning of the file, to match the synthesized file.
#    f_sig.write('\n')

    #allWrdPairs = []
    
    ## Clitics assigned at a higher level of the category hierarchy should get pushed down to sub-categories
    #push_clitics_down(catList, [], cat2CliticList, cat2Subcats)
    
    # Process each word and add affixes   # Disabled for now: and/or clitics  
    # Then output the full set of inflections for each word
    for wordPair in standardSpellList:

        catAndGuid = wordPair[1] # 2nd part of the tuple
        
        #report.Info('  Inflecting '+wordPair[0])
        # Inflect the words if there are templates for this category
        if catAndGuid in cat2Templ:
            inflWords = create_words_from_templates(wordPair, cat2Templ[catAndGuid], templ2Slots, slot2AffixList, slot2IsPrefix)
        else:
            continue
        #    If we wanted words without affixes, we would do the following as well
        #    inflWords = [wordPair[0]] # add this word; no need to add affixes
        
        # Temporarily, don't include clitics at all
        ## Add all clitics possible    
        #if catAndGuid in cat2CliticList:
        #    cliticList = cat2CliticList[catAndGuid]
        #    
        #    for myWordPr in inflWords:
        #        newPairs = []
        #        add_clitics(myWordPr, cliticList, newPairs)
        #        allWrdPairs.extend(newPairs)
        #else:
        #    allWrdPairs.extend(inflWords)

    # Iterate through the list of constructed words (for this stem) and output to all files
    
        # (It's not really a pair now.  When it was in allWrdPairs, it was a pair of word + POS info.)
        for inflectedWord in inflWords:
        #for inflectedWord in allWrdPairs:
            wrdCount += 1
            # Reset the variables
            sigPfxs = ufPfxs = pfxs = sigSfxs = ufSfxs = sfxs = rootString = rootGloss = rootForm = posLabel = ''

            #report.Info('Testing '+inflectedWord)            
            
            ##  Need to pick out the prefixes, gloss, root, POS, and suffixes from the string
            # First check for prefixes
            m = re.match('(<.+>)([^<][^<>]+<[^<>]+>.*)', inflectedWord)
            if m:
                # This string has prefixes, so store them and remove from inflectedWord
                pfxs = m.group(1)
                rest = m.group(2)
                #report.Info('pfxs = ['+pfxs+']  rest = ['+rest+']')
            else:
                pfxs = ''
                rest = inflectedWord
            
            # Now check for suffixes
            m = re.match('([^<][^<>]+<[^<>]+>)(<.+>)', rest)
            if m:
                # This string has suffixes, so store them and remove from rest
                rootString = m.group(1)
                sfxs = m.group(2)
            else:
                sfxs = ''
                rootString = rest
                
            # Still need to validate the Root part is valid, and get parts
            m = re.match('(\[[^\]]+\])([^<][^<>]+)<([^<>]+)>', rootString)
            if m:
                # Match the gloss part
                rootGloss = m.group(1)
                # Match the root part
                rootForm = m.group(2)
                ## Remove the homograph number
                ## (Not doing this now: the Morphname in the dictionary includes it.)
                #rootForm = re.sub(r'\d+\.\d+','', rootForm)
                # Match the POS part
                posLabel = m.group(3)
            else:
                report.Error('Malformed root string: '+rootString)
            ## (Do we need to verify that there are no <> in any Glosses??)
                
            # Set values for the parses output file
            ufPfxs = pfxs
            ufSfxs = sfxs
                    
            # Output to the Apertium format first
            thisWord = '^'+rootForm+'<'+posLabel+'>'+pfxs+sfxs+'$'
            #report.Info("thisWord is "+thisWord)
            f_aper.write(thisWord+'\n')
            thisWord = ''

## Uncomment this section if we want to write the .ana file directly, and SIGMORPHON format
#            # For the ANA file, reformat the root to be in angle brackets with the POS before it
#            rootString = '< '+posLabel+' '+rootForm+' >'
#            
#            # Reformat the affixes to not have angle brackets around them,
#            # for the ANA output, as well as others.
#
#            if pfxs:
#                # Save the prefixes for the SIGMORPHON format
#                sigPfxs = pfxs
#                # Save the prefixes for the parses (uf) format
#                ufPfxs = pfxs
#                # Format for ANA
#                pfxs = re.sub('>', ' ', pfxs)
#                pfxs = re.sub('<', '', pfxs)
#            if sfxs:
#                # Save the suffixes for the SIGMORPHON format
#                sigSfxs = sfxs
#                # Save the suffixes for the parses (uf) format
#                ufSfxs = sfxs
#                # Format for ANA
#                sfxs = re.sub('<', ' ', sfxs)
#                sfxs = re.sub('>', '', sfxs)
#
#           # Write the SF codes and the output strings
#            # The \f marker is for "following punctuation".  (or is it "preceding"?)
#            # We want each word 
#            # to be followed by a newline in the synthesized output.
#            f_ana.write('\\a '+pfxs+rootString+sfxs+'\n\\f \\n\n\n')

#          # Uncomment this section if we are doing SIGMORPHON format
#            # Format for SIG
#            if sigPfxs:
#                sigPfxs = re.sub(r'[>{}]', '', sigPfxs)
#                sigPfxs = re.sub('<', ';', sigPfxs)
#            if sigSfxs:
#                sigSfxs = re.sub(r'[>{}]', '', sigSfxs)
#                sigSfxs = re.sub('<', ';', sigSfxs)
#
#            # Write the SIGMORPHON style output
#            f_sig.write(posLabel.upper()+sigPfxs.upper()+sigSfxs.upper()+'\n')

            ## Format the Glosses (parses) output string and write it
            # Remove the Citation Form of the root and the homograph/sense number,
            # leaving the Gloss of the root, with the affixes
            # Using the affixes with < > around them currently.
            #glosses = re.sub(r'\][^1-9]+1\.1', ']', inflectedWord)
            #f_out.write(glosses + '\n')
            f_out.write(ufPfxs+rootGloss+'<'+posLabel+'>'+ufSfxs+'\n')


    ## Output final counts to the log file.
    f_log.write('\n\n'+str(wrdCount)+' words generated.'+'\n')

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
