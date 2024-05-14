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
        self.lemmaMacros = {} # {(pos, [(cat, label, affix), ...]): (macro_name, var_name, pos_sequence)}

        # XML validation forces macro, category, etc. IDs
        # to all be in the same namespaces, so track them all together
        self.usedIDs = set()

    def ProcessExistingTransferFile(self, fileName):
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(fileName, parser=parser)
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
        self.usedIDs.add(start)
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

            catEl = ET.SubElement(section, 'def-cat', n=cid)
            ET.SubElement(catEl, 'cat-item', tags=category)
            ET.SubElement(catEl, 'cat-item', tags=category+'.*')

    def AddSingleAttribute(self, suggested_name, items, comment=None,
                           subset_ok=False):
        for name, values in self.definedAttributes.items():
            if values == items or (subset_ok and items < values):
                return name

        aid = self.GetAvailableID(suggested_name)
        section = self.root.find('section-def-attrs')
        if comment:
            section.append(ET.Comment(comment))
        elem = ET.SubElement(section, 'def-attr', n=aid)
        for tag in sorted(items):
            ET.SubElement(elem, 'attr-item', tags=tag)
        self.definedAttributes[aid] = items
        return aid

    def EnsureAttribute(self, category, label, isAffix):
        if (category, label) in self.featureToAttributeName:
            return self.featureToAttributeName[(category, label)]

        if isAffix:
            values = set([Utils.underscores(l[0])
                          for l in Utils.getAffixGlossesForFeature(
                                  self.DB, self.report, self.configMap,
                                  category, label)])
        else:
            values = set([Utils.underscores(l[1])
                          for l in Utils.getLemmasForFeature(
                                  self.DB, self.report, self.configMap,
                                  category, label)])

        if isAffix:
            name = f'a_{category}_{label}'
        else:
            name = f'a_{label}'
        aid = self.AddSingleAttribute(name, values)
        self.featureToAttributeName[(category, label)] = aid
        return aid

    def AddVariable(self, name, comment=None):
        def GetIndex(section, name):
            # If there is a variable that is lexicographically after the one
            # that we're adding, we want to insert the new variable immediately
            # after the previous variable (assuming that comments generally
            # apply to the element that follows them).
            last = 0
            for index, node in enumerate(section):
                if node.tag == 'def-var':
                    n = node.get('n')
                    if n and n > name:
                        return last
                else:
                    last = index
            # However, if there is no following variable, we want to skip any
            # trailing comments, so we put it at the very end.
            return len(section)

        section = self.root.find('section-def-vars')
        loc = GetIndex(section, name)

        if comment:
            section.insert(loc, ET.Comment(comment))
            loc += 1
        section.insert(loc, ET.Element('def-var', n=name))

    def GetTags(self, category, label, isAffix):
        # Return a set of tuples where the first element is the tag that
        # would appear in the stream and the second element is the feature
        # value so that we can match it up with the tags for other categories.
        if isAffix:
            return set([(Utils.underscores(l[0]), Utils.underscores(l[1]))
                        for l in Utils.getAffixGlossesForFeature(
                                self.DB, self.report, self.configMap,
                                category, label)])
        else:
            # If we're getting lemma features, they will show up as their
            # values, so we discard the actual lemmas.
            return set([(Utils.underscores(l[1]), Utils.underscores(l[1]))
                        for l in Utils.getLemmasForFeature(
                                self.DB, self.report, self.configMap,
                                category, label)])

    def GetAttributeMacro(self, srcSpec, trgSpec):
        if (srcSpec, trgSpec) in self.attributeMacros:
            return self.attributeMacros[(srcSpec, trgSpec)]

        src = self.GetTags(*srcSpec)
        trg = self.GetTags(*trgSpec)

        if src == trg:
            self.attributeMacros[(srcSpec, trgSpec)] = (None, None)
            return (None, None)

        macid = self.GetAvailableID(f'm_{srcSpec[0]}_{srcSpec[1]}-to-{trgSpec[0]}_{trgSpec[1]}')
        varid = self.GetAvailableID(f'v_{trgSpec[0]}_{trgSpec[1]}')
        self.AddVariable(varid, f'Used by macro {macid}')
        macro = ET.SubElement(self.root.find('section-def-macros'), 'def-macro',
                              n=macid, npar='1')

        macro.append(ET.Comment("Clear the variable to be sure we don't accidentally retain a prior value"))
        let1 = ET.SubElement(macro, 'let')
        ET.SubElement(let1, 'var', n=varid)
        ET.SubElement(let1, 'lit', v='')

        choose = ET.SubElement(macro, 'choose')
        for srcTag, srcFeat in src:
            when = ET.SubElement(choose, 'when')
            test = ET.SubElement(when, 'test')
            eq = ET.SubElement(test, 'equal')
            ET.SubElement(eq, 'clip', pos='1', side='tl',
                          part=self.EnsureAttribute(*srcSpec))
            ET.SubElement(eq, 'lit-tag', v=srcTag)

            wlet = ET.SubElement(when, 'let')
            ET.SubElement(wlet, 'var', n=varid)

            for trgTag, trgFeat in trg:
                if trgFeat == srcFeat:
                    ET.SubElement(wlet, 'lit-tag', v=trgTag)
                    break
            else:
                ET.SubElement(wlet, 'lit-tag', v=f'{srcFeat}_NOTAG')

        otherwise = ET.SubElement(choose, 'otherwise')
        olet = ET.SubElement(otherwise, 'let')
        ET.SubElement(olet, 'var', n=varid)
        ET.SubElement(olet, 'lit-tag', v=f'{trgSpec[1]}_UNK')

        self.attributeMacros[(srcSpec, trgSpec)] = (macid, varid)
        return (macid, varid)

    def GetLemmaMacro(self, destCategory, sources):
        catSequence = sorted(set([s[0] for s in sources]))
        lookupKey = (destCategory, tuple(catSequence))
        if lookupKey in self.lemmaMacros:
            return self.lemmaMacros[lookupKey]

        label = f'{destCategory}_lemma_from_{"-".join(catSequence)}'
        macid = self.GetAvailableID('m_'+label)
        varid = self.GetAvailableID('v_'+label)
        self.AddVariable(varid, f'Used by macro {macid}')
        macro = ET.SubElement(self.root.find('section-def-macros'), 'def-macro',
                              n=macid, npar=str(len(catSequence)))

        def SetVar(parent, value):
            nonlocal varid
            let = ET.SubElement(parent, 'let')
            ET.SubElement(let, 'var', n=varid)
            ET.SubElement(let, 'lit', v=value)

        macro.append(ET.Comment("Clear the variable to be sure we don't accidentally retain a prior value"))
        SetVar(macro, '')

        labelSeq = [s[1] for s in sources]
        locations = [(macro, None, [])]
        for category, label, isAffix in sources:
            clipPos = str(catSequence.index(category)+1)
            tags = sorted(self.GetTags(category, label, isAffix))
            allLemmas = Utils.getLemmasForFeature(
                self.DB, self.report, self.configMap, destCategory, label)
            newLocations = []

            for elem, possibleLemmas, path in locations:
                lemmas = allLemmas
                if possibleLemmas is not None:
                    lemmas = [l for l in allLemmas if l[0] in possibleLemmas]

                if not lemmas:
                    SetVar(elem, 'no_lemma_for_'+'_'.join(path))
                    continue

                given = ''
                if path:
                    specs = [f'{label} = {value}' for label, value in zip(labelSeq, path)]
                    given = f' given {", ".join(specs)}'
                elem.append(ET.Comment(f'Narrow the set of possible lemmas based on {label}{given}.'))
                choose = ET.SubElement(elem, 'choose')
                for tag, feature in tags:
                    when = ET.SubElement(choose, 'when')
                    test = ET.SubElement(when, 'test')
                    eq = ET.SubElement(test, 'equal')
                    ET.SubElement(
                        eq, 'clip', pos=clipPos, side='tl',
                        part=self.EnsureAttribute(category, label, isAffix))
                    ET.SubElement(eq, 'lit-tag', v=tag)
                    nextLemmas = set(l[0] for l in lemmas if l[1] == feature)
                    newLocations.append((when, nextLemmas, path+[feature]))

                SetVar(ET.SubElement(choose, 'otherwise'),
                       'no_lemma_for_'+'_'.join(path))

            locations = newLocations

        for elem, possibleLemmas, path in locations:
            error = 'lemma_for_' + '_'.join(path)
            if len(possibleLemmas) == 0:
                value = 'no_'+error
            elif len(possibleLemmas) == 1:
                value = list(possibleLemmas)[0]
            else:
                lemmas = ', '.join(sorted(possibleLemmas))
                elem.append(ET.Comment(f'Possible lemmas with this combination of tags: {lemmas}'))
                value = 'multiple_'+error
            SetVar(elem, value)

        self.lemmaMacros[lookupKey] = (macid, varid, catSequence)
        return (macid, varid, catSequence)

    def ProcessRule(self, rule):
        ruleName = rule.get('name')
        if ruleName in self.ruleNames:
            self.report.Error(f'Rule name "{ruleName}" already exists in the rule file.')
            return

        ruleEl = ET.SubElement(self.root.find('section-rules'), 'rule',
                               comment=ruleName)
        self.ruleNames.add(ruleName)

        wordCats = {}
        patternEl = ET.SubElement(ruleEl, 'pattern')
        for word in rule.findall('.//Source//Word'):
            wid = word.get('id')
            cat = word.get('category')
            ET.SubElement(patternEl, 'pattern-item', n=self.tagToCategoryName[cat])
            wordCats[wid] = cat

        actionEl = ET.SubElement(ruleEl, 'action')

        outEl = ET.Element('out')

        usedMacros = set()

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

            lemmaTags = []
            lemmaLocs = {}
            for feature in word.findall('./Features/Feature'):
                label = feature.get('label')
                match = feature.get('match')
                apos, isAffix = featureSources.get((label, match), pos)
                lemmaTags.append((wordCats[apos], label, isAffix))
                lemmaLocs[wordCats[apos]] = apos
            shouldUseLemmaMacro = lemmaTags and lemmaLocs != {cat:pos}

            # TODO: check that it's not a proper noun
            if index == 0 and (pos != '1' or shouldUseLemmaMacro):
                lemCase = ET.SubElement(lu, 'get-case-from', pos='1')
            elif index > 0 and pos == '1':
                lemCase = ET.SubElement(lu, 'get-case-from', pos=str(index+1))
            else:
                lemCase = lu

            if shouldUseLemmaMacro:
                macid, varid, catSequence = self.GetLemmaMacro(cat, lemmaTags)
                if macid not in usedMacros:
                    actionEl.append(ET.Comment(f'Determine the appropriate lemma for {cat} and store it in a variable named {varid}.'))
                    callmac = ET.SubElement(actionEl, 'call-macro', n=macid)
                    for srcCat in catSequence:
                        ET.SubElement(callmac, 'with-param',
                                      pos=lemmaLocs[srcCat])
                    usedMacros.add(macid)
                ET.SubElement(lemCase, 'var', n=varid)
            else:
                ET.SubElement(lemCase, 'clip', pos=pos, side='tl', part='lem')

            ET.SubElement(
                lu, 'clip', pos=pos, side='tl', part=self.categoryAttribute,
            )
            for affix in word.findall('.//Affix//Feature'):
                label = affix.get('label')
                match = affix.get('match')
                apos, isAffix = featureSources.get((label, match), pos)
                if apos != pos:
                    mac, var = self.GetAttributeMacro(
                        (wordCats[apos], label, isAffix),
                        (cat, label, True))
                    if mac is not None:
                        if mac not in usedMacros:
                            actionEl.append(ET.Comment(f'Determine the appropriate {label} tag for {cat} and store it in a variable named {var}.'))
                            callmac = ET.SubElement(actionEl, 'call-macro',
                                                    n=mac)
                            ET.SubElement(callmac, 'with-param', pos=apos)
                            usedMacros.add(mac)
                        ET.SubElement(lu, 'var', n=var)
                        continue
                attr = self.EnsureAttribute(cat, label, True)
                ET.SubElement(lu, 'clip', pos=apos, side='tl', part=attr)

        actionEl.append(outEl)

    def ProcessAssistantFile(self, fileName):
        tree = ET.parse(fileName)
        root = tree.getroot()

        if self.root is None:
            self.CreateTree()

        self.AddCategories(root)

        self.categoryAttribute = self.AddSingleAttribute(
            'a_gram_cat', set(self.tagToCategoryName.keys()),
            comment='Part-of-speech tags used in the rules', subset_ok=True)

        for rule in root.findall('.//FLExTransRule'):
            self.ProcessRule(rule)

    def WriteTransferFile(self, fileName):
        with open(fileName, 'wb') as fout:
            fout.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf-8'))
            fout.write('<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN" "transfer.dtd">\n'.encode('utf-8'))
            node = MD.parseString(ET.tostring(self.root)).firstChild
            txt = node.toprettyxml(indent='\t', encoding='utf-8')
            fout.write(txt)

# Wrapper function which calls the necessary logic to write rules to the Aperitum file
def CreateRules(DB, report, configMap, ruleAssistantFile, transferRulePath):

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

    generator = RuleGenerator(DB, report, configMap)

    if os.path.exists(transferRulePath):
        # TODO change to more informative name
        backupPath = f'{transferRulePath}.{int(time.time())}.bak'
        report.Info(f'Copying prior version of transfer rules to {backupPath}.')
        shutil.copy(transferRulePath, backupPath)
        generator.ProcessExistingTransferFile(transferRulePath)

    generator.ProcessAssistantFile(ruleAssistantFile)

    generator.WriteTransferFile(transferRulePath)

    return True

