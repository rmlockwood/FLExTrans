#
#   CreateApertiumRules
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 3.9.x - 11/06/23 - Matthew Fort
#    First draft version of reading in, checking, writing
#
#   Version 3.9 - 9/11/23 - Ron Lockwood
#    Initial version
#
#   Given an xml file defining the rules, create Apertium-style rules

import Utils

import re
import os
import unicodedata
import shutil
import time
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
from collections import defaultdict

class RuleGenerator:
    def __init__(self, DB, report, configMap):
        self.DB = DB
        self.report = report
        self.configMap = configMap

        self.root = None

        self.definedCategories = {} # {name: [(lemma, tags), ...]}
        self.definedAttributes = {} # {name: [tags, ...]}
        self.tagToCategoryName = {} # {category: attribute}
        self.featureToAttributeName = {} # {(category, label): attribute}
        self.categoryAttribute = None

        self.variables = {} # {name: initial_value}
        self.lists = {} # {name: [value, ...]}
        self.ruleNames = set()

        self.attributeMacros = {} # {((cat, label, affix), (cat, label, affix)): (macro_name, var_name)}

        # XML validation forces macro, category, etc. IDs
        # to all be in the same namespaces, so track them all together
        self.usedIDs = set()

    def processExistingTransferFile(self, fileName):
        tree = ET.parse(fileName)
        self.root = tree.getroot()

        for cat in self.root.findall('.//def-cat'):
            name = cat.get('n')
            items = [(i.get('lemma'), i.get('tags')) for i in cat.findall('./cat-item')]
            self.usedIDs.add(name)
            self.definedCategories[name] = items

            if len(items) == 2:
                if not items[0][0] and not items[1][0]: # no lemmas
                    ls = sorted([items[0][1], items[1][1]])
                    if ls[1] == ls[0] + '.*':
                        self.tagToCategoryName[ls[0]] = name

        for attr in self.root.findall('.//def-attr'):
            name = attr.get('n')
            values = set([i.get('tags') for i in attr.findall('./attr-item')])
            self.usedIDs.add(name)
            self.definedAttributes[name] = values

        for var in self.root.findall('.//def-var'):
            name = var.get('n')
            val = var.get('v')
            self.usedIDs.add(name)
            self.variables[name] = val

        for lst in self.root.findall('.//def-list'):
            name = lst.get('n')
            values = [i.get('v') for i in lst.findall('./list-item')]
            self.usedIDs.add(name)
            self.lists[name] = values

        for macro in self.root.findall('.//def-macro'):
            self.usedIDs.add(macro.get('n'))

        for rule in self.root.findall('.//rule'):
            self.ruleNames.add(rule.get('comment'))

    def CreateTree(self):
        self.root = ET.Element('transfer')

        for section in ['section-def-cats', 'section-def-attrs', 'section-def-vars', 'section-def-macros', 'section-rules']:
            ET.SubElement(self.root, section)

    def GetAvailableID(self, start):
        while start in self.usedIDs:
            start += '_'
        return start

    def AddCategories(self, root):
        section = self.root.find('section-def-cats')
        for node in root.findall('.//Source//Word'):
            category = node.get('category')
            if not category or category in self.tagToCategoryName:
                continue
            cid = self.GetAvailableID('c_'+category)
            self.definedCategories[cid] = [(None, category), (None, category+'.*')]
            self.tagToCategoryName[category] = cid
            self.usedIDs.add(cid)

            catEl = ET.SubElement(section, 'def-cat', {'n': cid})
            ET.SubElement(catEl, 'cat-item', {'tags': category})
            ET.SubElement(catEl, 'cat-item', {'tags': category+'.*'})

    def AddSingleAttribute(self, suggested_name, items):
        for name, values in self.definedAttributes.items():
            if values == items:
                return name

        aid = self.GetAvailableID(suggested_name)
        self.usedIDs.add(aid)
        section = self.root.find('section-def-attrs')
        elem = ET.SubElement(section, 'def-attr', {'n': aid})
        for tag in sorted(items):
            ET.SubElement(elem, 'attr-item', {'tags': tag})
        self.definedAttributes[aid] = items
        return aid

    def EnsureAttribute(self, category, label, isAffix):
        if (category, label) in self.featureToAttributeName:
            return self.featureToAttributeName[(category, label)]

        if isAffix:
            values = set([l[0] for l in Utils.getAffixGlossesForFeature(
                self.DB, self.report, self.configMap, category, label)])
        else:
            values = set([l[1] for l in Utils.getLemmasForFeature(
                self.DB, self.report, self.configMap, category, label)])

        if isAffix:
            name = f'a_{category}_{label}'
        else:
            name = f'a_{label}'
        aid = self.AddSingleAttribute(name, values)
        self.featureToAttributeName[(category, label)] = aid
        return aid

    def getTags(self, category, label, isAffix):
        if isAffix:
            return set(Utils.getAffixGlossesForFeature(
                self.DB, self.report, self.configMap, category, label))
        else:
            return set([(l[1], l[1]) for l in Utils.getLemmasForFeature(
                self.DB, self.report, self.configMap, category, label)])

    def getAttributeMacro(self, srcSpec, trgSpec):
        if (srcSpec, trgSpec) in self.attributeMacros:
            return self.attributeMacros[(srcSpec, trgSpec)]

        src = self.getTags(*srcSpec)
        trg = self.getTags(*trgSpec)

        if src == trg:
            self.attributeMacros[(srcSpec, trgSpec)] = (None, None)
            return (None, None)

        macid = self.GetAvailableID(f'm_{srcSpec[0]}_{srcSpec[1]}-to-{trgSpec[0]}_{trgSpec[1]}')
        varid = self.GetAvailableID(f'v_{trgSpec[0]}_{trgSpec[1]}')
        ET.SubElement(self.root.find('section-def-vars'), 'def-var',
                      {'n':varid, 'c':f'Used by macro {macid}'})
        macro = ET.SubElement(self.root.find('section-def-macros'), 'def-macro',
                              {'n':macid, 'npar':'1'})

        # strictly speaking, clearing the variable like this is unnecessary
        # but it might be useful as a signal to the reader
        let1 = ET.SubElement(macro, 'let')
        ET.SubElement(let1, 'var', {'n':varid})
        ET.SubElement(let1, 'lit', {'v':''})

        choose = ET.SubElement(macro, 'choose')
        for srcTag, srcFeat in src:
            when = ET.SubElement(choose, 'when')
            test = ET.SubElement(when, 'test')
            eq = ET.SubElement(test, 'equal')
            ET.SubElement(eq, 'clip', {'pos':'1', 'side':'tl',
                                       'part':self.EnsureAttribute(*srcSpec)})
            ET.SubElement(eq, 'lit-tag', {'v':srcTag})

            wlet = ET.SubElement(when, 'let')
            ET.SubElement(wlet, 'var', {'n':varid})

            for trgTag, trgFeat in trg:
                if trgFeat == srcFeat:
                    ET.SubElement(wlet, 'lit-tag', {'v':trgTag})
                    break
            else:
                ET.SubElement(wlet, 'lit-tag', {'v':f'{srcFeat}_NOTAG'})

        otherwise = ET.SubElement(choose, 'otherwise')
        olet = ET.SubElement(otherwise, 'let')
        ET.SubElement(olet, 'var', {'n':varid})
        ET.SubElement(olet, 'lit-tag', {'v':f'{trgSpec[1]}_UNK'})

        self.attributeMacros[(srcSpec, trgSpec)] = (macid, varid)
        return (macid, varid)

    def ProcessRule(self, rule):
        ruleName = rule.get('name')
        if ruleName in self.ruleNames:
            self.report.Error(f'Rule name "{ruleName}" already exists in the rule file.')
            return

        ruleEl = ET.SubElement(self.root.find('section-rules'), 'rule',
                               {'comment': ruleName})
        self.ruleNames.add(ruleName)

        wordCats = {}
        patternEl = ET.SubElement(ruleEl, 'pattern')
        for word in rule.findall('.//Source//Word'):
            wid = word.get('id')
            cat = word.get('category')
            ET.SubElement(patternEl, 'pattern-item', {'n': cat})
            wordCats[wid] = cat

        actionEl = ET.SubElement(ruleEl, 'action')

        outEl = ET.Element('out')

        usedMacros = set()

        # TODO: construct and track macros for replacing lemmas
        # TODO: construct and track macros for renaming features

        matches = defaultdict(list)
        for index, word in enumerate(rule.findall('.//Target//Word')):
            head = (word.get('head') == 'yes')
            wid = word.get('id')
            for feat in word.findall('./Features/Feature'):
                matches[(feat.get('label'), feat.get('match'))].append(
                    (wid, head, False))
            for feat in word.findall('.//Affix//Feature'):
                matches[(feat.get('label'), feat.get('match'))].append(
                    (wid, head, True))

        featureSources = {}
        for (label, match), items in matches.items():
            cur = None
            for wid, head, affix in items:
                if head:
                    cur = (wid, affix)
                    break
                elif not affix and cur is None:
                    cur = (wid, affix)
            if cur is None:
                self.report.Error(f'Unable to determine source for {match} {label} in {ruleName}.')
            else:
                featureSources[(label, match)] = cur

        for index, word in enumerate(rule.findall('.//Target//Word')):
            if index > 0:
                ET.SubElement(outEl, 'b')
            lu = ET.SubElement(outEl, 'lu')
            pos = word.get('id') # TODO: validate ID sequencing
            cat = wordCats[pos] # TODO: what if it's an inserted word?
            ET.SubElement(lu, 'clip', {'pos':pos, 'side':'tl', 'part':'lem'})
            ET.SubElement(
                lu, 'clip',
                {'pos':pos, 'side':'tl', 'part':self.categoryAttribute},
            )
            for affix in word.findall('.//Affix//Feature'):
                label = affix.get('label')
                match = affix.get('match')
                apos, isAffix = featureSources.get((label, match), pos)
                if apos != pos:
                    mac, var = self.getAttributeMacro(
                        (wordCats[apos], label, isAffix),
                        (cat, label, True))
                    if mac is not None:
                        if mac not in usedMacros:
                            callmac = ET.SubElement(actionEl, 'call-macro',
                                                    {'n': mac})
                            ET.SubElement(callmac, 'with-param', {'pos':apos})
                            usedMacros.add(mac)
                        ET.SubElement(lu, 'var', {'n':var})
                        continue
                attr = self.EnsureAttribute(cat, label, True)
                ET.SubElement(lu, 'clip', {'pos':apos, 'side':'tl', 'part':attr})

        actionEl.append(outEl)

    def ProcessAssistantFile(self, fileName):
        tree = ET.parse(fileName)
        root = tree.getroot()

        if self.root is None:
            self.CreateTree()

        self.AddCategories(root)

        self.report.Info(str(self.tagToCategoryName))

        self.categoryAttribute = self.AddSingleAttribute(
            'a_gram_cat', set(self.tagToCategoryName.keys()))

        for rule in root.findall('.//FLExTransRule'):
            self.ProcessRule(rule)

        self.report.Info(str(self.featureToAttributeName))

    def WriteTransferFile(self, fileName):
        with open(fileName, 'wb') as fout:
            txt = MD.parseString(ET.tostring(self.root)).toprettyxml(indent='\t')
            fout.write(txt.encode('utf-8'))

# NOTE: this version is tested on writing to an *empty* apertium file, rename 'transfer_rules.t1x' to try running this, however a backup will be created before anything else is run

# Builds a new .t1x file if one is not given from the user
def CreateNewApertiumTree():
    apertiumAttributes = ['section-def-cats', 'section-def-attrs', 'section-def-vars', 'section-def-macros', 'section-rules']

    apertiumRoot = ET.Element('transfer')

    for section in apertiumAttributes:
        ET.SubElement(apertiumRoot, section)

    return ET.ElementTree(apertiumRoot)

# Check categories and attributes referenced in the ruleAssistantFiles
# FIXME: refactor all this - will not work
def CheckAssistantFile(report, apertiumTree, assistantTree):
    apertiumRoot = apertiumTree.getroot()

    apertiumTreeAttributes = []
    apertiumTreeCategories = []
    assistantTreeAttributes = []
    assistantTreeCategories = []

    # Get the attributes from the Apertium transfer file
    for attribute in apertiumRoot.iter('cat-item'):
        apertiumTreeAttributes.append(attribute.get('tags'))

    # Get the categories from the Apertium trasnfer file
    for category in apertiumRoot.iter('attr-item'):
        apertiumTreeCategories.append(category.get('tags'))

    # Get the attributes from the RuleAssistant file
    # TODO: ensure this is the correct info
    for attribute in assistantTree.findall('.//Target//Feature'):
        assistantTreeAttributes.append(attribute.get('label'))

    # Get the category from the RuleAssistant file
    # TODO: ensure this is the correct info
    for category in assistantTree.findall('.//Source//Word'):
        assistantTreeCategories.append(category.get('category'))

    # Check to see if there's a category or attribute in the RuleAssistant File
    # which isn't in the Apertium transfer file
    # TODO: Ensure the compared categories and features are truly the ones needed
    # if (list(set(assistantTreeCategories) - set(apertiumTreeCategories))) \
    #     or (list(set(assistantTreeAttributes) - set(apertiumTreeAttributes))):
    #     return -1

    return 0

# Add the information within the <section-def-cats> in the Apertium t1x file
# TODO: Ensure this works if there already exists an Apertium file (look for overwrites, redundancies, etc)
# TODO: This can also be done by pulling from the Utils file - but this should be robust as the AssistantFile is built from FLEx...
def AddCategories(report, apertiumTree, assistantTree):
    apertiumCategoryNode = apertiumTree.getroot().find('.//section-def-cats')

    for words in assistantTree.findall('.//Source//Word'):
        # Check to see if the category is already classified
        # TODO: move lower
        if apertiumCategoryNode.find('.//cat-item') and \
            apertiumCategoryNode.find('.//cat-item').get('tags') == words.get('category'):
            continue

        # Check to see if there already exists a defined category for the categorical label
        # TODO: check logic here
        if apertiumCategoryNode.find(".//def-cat[@n='" + words.get('category') + "']") is not None:
            pass
        else:
            ET.SubElement(apertiumCategoryNode, 'def-cat')
            for definedCategories in apertiumCategoryNode.iter('def-cat'):
                if not definedCategories.get('n'):
                    definedCategories.set('n', 'c_' + words.get('category'))
                    tags = words.get('category', '*')
                    ET.SubElement(definedCategories, 'cat-item',
                                  attrib={'tags': tags})
                    if tags != '*':
                        ET.SubElement(definedCategories, 'cat-item',
                                      attrib={'tags': tags+'.*'})

    return apertiumTree

# Adds the information within the <section-def-attrs> in the Apertium t1x file
def AddAttributes(DB, report, configMap, apertiumTree, assistantTree):
    apertiumAttributeNode = apertiumTree.getroot().find('.//section-def-attrs')

    for features in assistantTree.findall('.//Target//Feature'):
        # Check to see if the attribute is already classified
        # TODO: move lower - check the lower level after the upper level
        # if apertiumAttributeNode.find('.//attr-item') and \
        #     apertiumAttributeNode.find(".//attr-item[@n='" + features.get('label') + "']"):
        #     continue 
        # report.Info(".//def-attr[@n='a_" + features.get('label') + "']")
        # Check to see if there already exists a defined attribute for the attribute label
        # TODO: check the logic here
        if apertiumAttributeNode.find(".//def-attr[@n='a_" + features.get('label') + "']") is not None:
            pass
        else:
            ET.SubElement(apertiumAttributeNode, 'def-attr')
            for definedAttributes in apertiumAttributeNode.iter('def-attr'):
                if not definedAttributes.get('n'):
                    definedAttributes.set('n', 'a_' + features.get('label'))

                    # add the tags, so get the lemmas from Utils
                    attributeList = set()
                    for words in assistantTree.findall('.//Source//Word'):
                        lemmas = Utils.getLemmasForFeature(DB, report, configMap, words.get('category'), features.get('label'))
                        for lemma in lemmas:
                            attributeList.add(lemma[1])

                    # add the attributes to the Apertium file
                    for attribute in list(attributeList):
                        if definedAttributes.find("./attr-item[@tags='" + attribute + "']") is None:
                            ET.SubElement(definedAttributes, 'attr-item')
                            definedAttributes.find('./attr-item[last()]').set('tags', attribute)

    return apertiumTree

# The largest burden of logic is here (i.e. the contents of the <action> tags)
# FIXME: finish the generalization of logic through this part of the file
def AddAction(DB, report, configMap, apertiumTree, assistantTree, apertiumRuleNode):
    # set up the wrapper around these procedures
    ET.SubElement(apertiumRuleNode, 'action')

    # TODO: generalize this to get all features from all the word features in the target phrase
    feature = assistantTree.find('.//Feature')

    # Get the unique lemmas for the feature relevant for the label specified in the assistant file
    attributeList = set()
    for words in assistantTree.findall('.//Source//Word'):
        lemmas = Utils.getLemmasForFeature(DB, report, configMap, words.get('category'), feature.get('label'))
        for lemma in lemmas:
            attributeList.add(lemma[1])
    attributeList = list(attributeList)

    # find the location of the head in the target phrase for the Apertium positional argument
    targetPhraseWords = assistantTree.find('.//Target//Words')
    head_pos = 1
    for word in targetPhraseWords:
        if word.get('head') == 'yes':
            break
        else:
            head_pos += 1

    # build the choose-when blocks as we encounter them
    # TODO: check logic to determine how many 'choose-when' blocks are needed
    if len(attributeList) > 1:
        ET.SubElement(apertiumRuleNode.find('./action'), 'choose')

    # We have the number of attributes, so we will iterate through all but the last to form sub-when blocks
    for attribute in attributeList[:-1]:

        # TODO: make generic and clean up
        # Build up the various Apertium sub-nodes for the choose-when block
        ET.SubElement(apertiumRuleNode.find('./action/choose'), 'when')
        whenNode = apertiumRuleNode.find(".//action/choose/when[last()]")
        ET.SubElement(whenNode, 'test')
        ET.SubElement(whenNode.find('./test'), 'equal')
        ET.SubElement(whenNode.find('./test/equal'), 'clip')
        ET.SubElement(whenNode.find('./test/equal'), 'lit-tag')

        # TODO: make generic by converting this to a function which will process whether this needs to be a clip section or not
        # Add necessary information within the clip node within the Apertium file
        clipNode = whenNode.find('./test/equal/clip')
        clipNode.set('pos', str(head_pos))
        clipNode.set('side', 'tl')
        clipNode.set('part', 'a_' + assistantTree.find('.//Target//Feature').get('label'))

        # TODO: make generic, as this 
        # Add the necessary information within the lit-tag node within the Apertium file
        litTagNode = whenNode.find('./test/equal/lit-tag')
        litTagNode.set('v', attribute)

        # TODO: make generic, as there can be multiple <lu> elements, and it could just be a clip, instead of a <lit> tag
        # form the out node of the rule
        ET.SubElement(whenNode, 'out')
        ET.SubElement(whenNode.find('./out'), 'lu')
        ET.SubElement(whenNode.find('./out/lu'), 'get-case-from')
        ET.SubElement(whenNode.find('./out/lu/get-case-from'), 'lit')
        ET.SubElement(whenNode.find('./out/lu'), 'lit-tag')

    # TODO: Add the final otherwise block and labels on the 

    return apertiumTree

# The main cluster of logic to write to the Apertium file is here
def AddRule(DB, report, configMap, apertiumTree, assistantTree):
    # TODO: Clarify this process
    # TODO: Adjust code to write n rules if there are n rules in the assistant file
    apertiumRoot = apertiumTree.getroot()
    assistantRoot = assistantTree.getroot()

    # store a list of all Apertium rule names so we can check existence and uniqueness
    apertiumRuleNames = []
    for apertiumRules in apertiumRoot.iter('rule'):
        apertiumRuleNames.append(apertiumRules.get('comment'))

    # Get the rule name from the assistant file to prepare to copy it to the Apertium file
    for assistantRule in assistantRoot.iter('FLExTransRule'):
        
        # Check if name of rule already exists in t1x file, and update rule name accordingly
        assistantRuleName = assistantRule.get('name')
        if assistantRuleName in apertiumRuleNames:
            report.Error("An Aperitum rule already exists with the given Assistant rule name")
            return -1

        # Add a new rule to the Aperitum file
        ET.SubElement(apertiumRoot.find('section-rules'), 'rule')

        # Add the rule name to the Apertium file
        for rule in apertiumRoot.iter('rule'):
            if not rule.get('comment'):
                rule.set('comment', assistantRuleName)

    # Select the node on which we'd like to add information
    # TODO: change this if there are multiple rules which need to be written to the apertium file
    apertiumRuleNode = apertiumRoot.find(".//rule[@comment='" + assistantRuleName + "']")

    # Add the pattern from the Assistant file to the Apertium file
    ET.SubElement(apertiumRuleNode, 'pattern')
    for assistantWord in assistantRoot.findall('.//Source//Word'):
        ET.SubElement(apertiumRuleNode.find('.//pattern'), 'pattern-item')
        apertiumRuleNode.find('./pattern/pattern-item[last()]').set('n', assistantWord.get('category'))

    # Add the Categories to the Apertium file
    apertiumTree = AddCategories(report, apertiumTree, assistantTree)

    # Add the Attributes to the Apertium file
    apertiumTree = AddAttributes(DB, report, configMap, apertiumTree, assistantTree)

    # add the specific rule for each rule name
    apertiumTree = AddAction(DB, report, configMap, apertiumTree, assistantTree, apertiumRuleNode)

    # NOTE: probably won't be able to use macros with this t1x file

    return apertiumTree

# Wrapper function to display information needed for debugging purposes
def GetInfo(DB, report, configMap, apertiumTree, assistantTree):
    
    # Read Source Phrase into a list of dictionaries
    sourcePhrase = []
    for word in assistantTree.findall('.//Source//Word'):
        sourcePhrase.append(word.attrib)

    # Read Target Phrase into a list of dictionaries
    targetPhrase = []
    for word in assistantTree.findall('.//Target//Word'):
        # Need to read in the features contained in the 'Word' tag and in the 'Feature' tag, so we combine the two attribute dicts
        tmpWordFeatures = word.attrib
        tmpWordFeatures.update(word.find('.//Feature').attrib)
        targetPhrase.append(tmpWordFeatures)

    gramCategory = 'n'
    # gramCategory= 'def'
    # gramCategory= 'adj'
    featureAbbrev = 'gender'
    # Use this function to get a list of tuples (gloss, featureValue) for this category that have this feature assigned. 
    # An empty list is returned if there are errors.
    lemmaList = Utils.getLemmasForFeature(DB, report, configMap, gramCategory, featureAbbrev)
    glossList = Utils.getAffixGlossesForFeature(DB, report, configMap, gramCategory, featureAbbrev)

    report.Info("Target Phrase: " + str(targetPhrase))
    report.Info("Source Phrase: " + str(sourcePhrase))
    report.Info("Gloss list: " + str(glossList))
    report.Info("Lemma list: " + str(lemmaList))

# Wrapper function which calls the necessary logic to write rules to the Aperitum file
def CreateRules(DB, report, configMap, ruleAssistantFile, transferRulePath):

    # If there is a trasnfer rule file, read it in
    if (os.path.exists(transferRulePath)):
        # TODO check for proper reading mode ("w" or "wb")
        with open(transferRulePath, "r") as apertiumFile:
            apertiumTree = ET.parse(apertiumFile)

        # make an Apertium transfer rule backup
        # TODO change to more informative name
        shutil.copy(transferRulePath, transferRulePath + "." + str(int(time.time())) + ".bak")

    # If there isn't a transfer rule file, create one
    else:
        apertiumTree = CreateNewApertiumTree()

    # TODO check for proper reading mode ("w" or "wb")
    try:
        with open(ruleAssistantFile, "r") as rulesAssistant:
            assistantTree = ET.parse(rulesAssistant)
    except:
        report.Error("No Rule Assistant file found, please run the Set Up Transfer Rule Categories and Attributes tool")
        return -1

    # Check to make sure the attributes and features listed in the files match
    # TODO: Change this to a better check function - currently does not do anything
    # if CheckAssistantFile(report, apertiumTree, assistantTree):
    #     report.Error("Please run the Set Up Transfer Rule Categories and Attributes tool")
    #     return -1

    # Useful function to display needed debugging information
    GetInfo(DB, report, configMap, apertiumTree, assistantTree)

    # Wrapper function to add each new rule found in the assistant tree file
    apertiumTree = AddRule(DB, report, configMap, apertiumTree, assistantTree)

    # test to add a comment to the xml file
    # NOTE: works! copy code and add comments throughout the rest of the apertium file creation
    comment = ET.Comment('this is a test comment at the root level')
    apertiumTree.getroot().insert(0, comment)

    # write the new tree information to the XML file
    # current file location: "[DIRECTORY TO FLEx]\FLExTrans\WorkProjects\[PROJECT NAME]\Config\test.xml"
    # TODO: use the actual aperitum file (path above) for this
    with open("test.xml", "wb") as xmlFile:
        xmlString = MD.parseString(ET.tostring(apertiumTree.getroot())).toprettyxml(indent = '\t')
        xmlFile.write(xmlString.encode('utf-8'))

    return True