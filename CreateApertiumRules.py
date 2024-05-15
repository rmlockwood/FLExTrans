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
from collections import defaultdict
from typing import Optional
from itertools import chain, combinations

class RuleGenerator:

    SectionSequence = ['section-def-cats', 'section-def-attrs',
                       'section-def-vars', 'section-def-macros', 'section-rules']

    def __init__(self, DB, report, configMap):
        self.DB = DB
        self.report = report
        self.configMap = configMap

        self.root: Optional[ET.Element] = None

        # All current <def-cat>s
        # {name: [(lemma, tags), ...]}
        self.definedCategories: dict[str, list[tuple[str, str]]] = {}

        # All current <def-attr>s
        # {name: [tags, ...]}
        self.definedAttributes: dict[str, set[str]] = {}

        # Mapping from part-of-speech tags to <def-cat> names
        # {category: attribute}
        self.tagToCategoryName: dict[str, str] = {}

        # Mapping from part-of-speech + feature name to <def-attr> name
        # {(category, label): attribute}
        self.featureToAttributeName: dict[tuple[str, str], str] = {}

        # Name of the <def-attr> for part-of-speech tags
        self.categoryAttribute: Optional[str] = None

        # All current <def-var>s
        # {name: initial_value}
        self.variables: dict[str, Optional[str]] = {}

        # All current <def-list>s
        # {name: [value, ...]}
        self.lists: dict[str, set[str]] = {}

        # The names of all current rules
        self.ruleNames: set[str] = set()

        self.attributeMacros = {} # {((cat, label, affix), (cat, label, affix)): (macro_name, var_name)}
        self.lemmaMacros = {} # {(pos, [(cat, label, affix), ...]): (macro_name, var_name, pos_sequence)}

        # XML validation forces macro, category, etc. IDs
        # to all be in the same namespaces, so track them all together
        self.usedIDs = set()

        # The <section-*> elements of the XML tree
        self.sections: dict[str: ET.Element] = {}

    def GetSection(self, sectionName: str) -> ET.Element:
        '''Retrieve a section of the rule file, creating it if necessary.'''

        if sectionName in self.sections:
            return self.sections[sectionName]
        elem = self.root.find(sectionName)
        if elem is None:
            index = RuleGenerator.SectionSequence.index(sectionName)
            elem = ET.Element(sectionName)
            if index == 0:
                # it's the first section, so just insert it
                self.root.insert(0, elem)
            else:
                # ensure that the preceding section exists
                prevTag = RuleGenerator.SectionSequence[index-1]
                self.GetSection(prevTag)
                for i, el in enumerate(self.root):
                    if el.tag == prevTag:
                        self.root.insert(i+1, elem)
                        break
        self.sections[sectionName] = elem
        return elem

    def ProcessExistingTransferFile(self, fileName: str) -> None:
        '''Load an existing transfer file.'''

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
            values = set([i.get('v') for i in lst.findall('./list-item')])
            self.usedIDs.add(name)
            self.lists[name] = values

        for macro in self.root.findall('.//def-macro'):
            self.usedIDs.add(macro.get('n'))

        for rule in self.root.findall('.//rule'):
            self.ruleNames.add(rule.get('comment'))

    def CreateTree(self) -> None:
        '''Generate a blank Apertium transfer XML tree.'''

        self.root = ET.Element('transfer')

        for section in RuleGenerator.SectionSequence:
            self.sections[section] = ET.SubElement(self.root, section)

    def GetAvailableID(self, start: str) -> str:
        '''Check whether `start` is already in use as an XML ID. If it is,
        modify it until it is not. Mark the resulting ID as in-use.'''

        while start in self.usedIDs:
            start += '_'
        self.usedIDs.add(start)
        return start

    def AddCategories(self, root):
        section = self.GetSection('section-def-cats')
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

    def AddSingleAttribute(self, suggested_name: str, items: set[str],
                           comment: Optional[str] = None,
                           subset_ok: bool = False) -> str:
        for name, values in self.definedAttributes.items():
            if values == items or (subset_ok and items < values):
                return name

        aid = self.GetAvailableID(suggested_name)
        section = self.GetSection('section-def-attrs')
        if comment:
            section.append(ET.Comment(comment))
        elem = ET.SubElement(section, 'def-attr', n=aid)
        for tag in sorted(items):
            ET.SubElement(elem, 'attr-item', tags=tag)
        self.definedAttributes[aid] = items
        return aid

    def EnsureAttribute(self, category: str, label: str, isAffix: bool) -> str:
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

    def AddVariable(self, name: str, comment: Optional[str] = None) -> None:
        '''Add a variable definition to <section-def-vars>, attempting
        to keep the section alphabetical.'''

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

        section = self.GetSection('section-def-vars')
        loc = GetIndex(section, name)

        if comment:
            section.insert(loc, ET.Comment(comment))
            loc += 1
        section.insert(loc, ET.Element('def-var', n=name))
        self.variables[name] = None

    def GetTags(self, category: str, label: str,
                isAffix: bool) -> set[tuple[str, str]]:
        '''Return a set of tuples where the first element is the tag that
        would appear in the stream and the second element is the feature
        value so that we can match it up with the tags for other categories.'''

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
        macro = ET.SubElement(self.GetSection('section-def-macros'), 'def-macro',
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

    def GetLemmaMacro(self, destCategory: str,
                      sources: list[tuple[str, str, str]]) -> tuple[str, str, list[str]]:
        '''Find or generate the appropriate macro for changing the lemma of
        a word with part of speech `destCategory` based on a set of agreement
        features (`sources`). Return the macro name, the variable name, and
        the order of the arguments to the macro by part-of-speech tag.'''

        catSequence = sorted(set([s[0] for s in sources]))
        lookupKey = (destCategory, tuple(catSequence))
        if lookupKey in self.lemmaMacros:
            return self.lemmaMacros[lookupKey]

        label = f'{destCategory}_lemma_from_{"-".join(catSequence)}'
        macid = self.GetAvailableID('m_'+label)
        varid = self.GetAvailableID('v_'+label)
        self.AddVariable(varid, f'Used by macro {macid}')
        macro = ET.SubElement(self.GetSection('section-def-macros'), 'def-macro',
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

    def ProcessRule(self, rule: ET.Element, skip: Optional[set[str]] = None) -> bool:
        '''Convert a Rule Assistant <Rule> node `rule` to an Apertium <rule>
        node and append it to the current XML tree. Return whether a rule
        was created. Skip any words whose id field is in `skip`.'''

        sourceWords = []
        for word in rule.findall('.//Source//Word'):
            wid = word.get('id')
            cat = word.get('category')
            sourceWords.append((wid, cat))

        ruleName = rule.get('name')
        if skip is not None:
            ruleName += ': '
            ruleName += ' '.join([w[1] for w in sourceWords if w[0] not in skip])
        if ruleName in self.ruleNames:
            self.report.Error(f'Rule name "{ruleName}" already exists in the rule file.')
            return False

        ruleEl = ET.SubElement(self.GetSection('section-rules'), 'rule',
                               comment=ruleName)
        self.ruleNames.add(ruleName)

        wordCats = {}
        wordLocation = {}
        patternEl = ET.SubElement(ruleEl, 'pattern')
        index = 0
        for wid, cat in sourceWords:
            if skip and wid in skip:
                continue
            index += 1
            ET.SubElement(patternEl, 'pattern-item', n=self.tagToCategoryName[cat])
            wordLocation[wid] = str(index)
            wordCats[str(index)] = cat

        actionEl = ET.SubElement(ruleEl, 'action')

        outEl = ET.Element('out')

        usedMacros = set()

        matches = defaultdict(list)
        for index, word in enumerate(rule.findall('.//Target//Word')):
            head = (word.get('head') == 'yes')
            wid = word.get('id')
            if skip and wid in skip:
                continue
            pos = wordLocation.get(wid)
            for feat in word.findall('./Features/Feature'):
                matches[(feat.get('label'), feat.get('match'))].append(
                    (pos, head, False))
            for feat in word.findall('.//Affix//Feature'):
                matches[(feat.get('label'), feat.get('match'))].append(
                    (pos, head, True))

        # For each combination of feature and match set, find the best source,
        # where the head word is preferred, if available, and otherwise we
        # take the rightmost word that has it as a stem feature rather than
        # an affix (rightmost not for any theoretical reason, but simply
        # because that was the easiest way to structure the loop).
        # If no such source is found, report an error.
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

        index = -1
        for word in rule.findall('.//Target//Word'):
            wid = word.get('id')
            if skip and wid in skip:
                continue
            index += 1
            if index > 0:
                ET.SubElement(outEl, 'b')
            lu = ET.SubElement(outEl, 'lu')
            pos = wordLocation.get(wid)
            if pos is None:
                self.report.Error(f'Word insertion not currently supported (attempted in {ruleName}).')
                self.GetSection('section-rules').remove(ruleEl)
                return False
            cat = wordCats[pos]

            # If the stem features have a source that isn't this word,
            # we want to use a macro to check that we have the right lemma.
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

            # Force prefixes to be before suffixes
            prefixFeatures = []
            suffixFeatures = []
            for affix in word.findall('.//Affix'):
                prefix = (affix.get('type', 'suffix') == 'prefix')
                for feature in affix.findall('.//Feature'):
                    label = feature.get('label')
                    match = feature.get('match')
                    if prefix:
                        prefixFeatures.append((label, match))
                    else:
                        suffixFeatures.append((label, match))

            for label, match in prefixFeatures + suffixFeatures:
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

        return True

    def ProcessAssistantFile(self, fileName: str,
                             ruleNumber: Optional[int] = None) -> None:
        '''Process the Rule Assistant file `fileName` and generate Apertium
        transfer rules. If `ruleNumber` is specified, only generate the rule
        at that index.'''

        tree = ET.parse(fileName)
        root = tree.getroot()

        if self.root is None:
            self.CreateTree()

        self.AddCategories(root)

        self.categoryAttribute = self.AddSingleAttribute(
            'a_gram_cat', set(self.tagToCategoryName.keys()),
            comment='Part-of-speech tags used in the rules', subset_ok=True)

        ruleCount = 0
        for index, rule in enumerate(root.findall('.//FLExTransRule')):
            if ruleNumber is not None and index != ruleNumber:
                continue
            if rule.get('create_permutations', 'no') == 'yes':
                deletable = []
                for word in rule.findall('.//Source//Word'):
                    wid = word.get('id')
                    if word.get('head') == 'yes':
                        continue
                    elif rule.find(f".//Target//Word[@id='{wid}'][@head='yes']"):
                        continue
                    deletable.append(wid)
                for skip in chain.from_iterable(combinations(deletable, length) for length in range(len(deletable))):
                    if self.ProcessRule(rule, skip=set(skip)):
                        ruleCount += 1
            else:
                if self.ProcessRule(rule):
                    ruleCount += 1

        self.report.Info(f'Added {ruleCount} rule(s) from {fileName}.')

    def WriteTransferFile(self, fileName: str) -> None:
        '''Write the generated transfer rules XML to `fileName`.'''

        with open(fileName, 'wb') as fout:
            fout.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf-8'))
            fout.write('<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN" "transfer.dtd">\n'.encode('utf-8'))
            ET.indent(self.root)
            fout.write(ET.tostring(self.root, encoding='utf-8'))

# Wrapper function which calls the necessary logic to write rules to the Aperitum file
def CreateRules(DB, report, configMap, ruleAssistantFile, transferRulePath, ruleNumber):

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

    generator.ProcessAssistantFile(ruleAssistantFile, ruleNumber)

    generator.WriteTransferFile(transferRulePath)

    return True

