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
import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Optional
from itertools import chain, combinations, permutations
from dataclasses import dataclass

@dataclass(frozen=True)
class FeatureSpec:
    category: str
    label: str
    isAffix: bool
    value: Optional[str] = None
    default: Optional[str] = None
    isSource: bool = False
    ranking: Optional[int] = None

    @property
    def xmlLabel(self):
        ls = [self.category, self.label]
        if self.default:
            ls += ['or', self.default]
        return '_'.join(ls)

@dataclass
class MacroSpec:
    macid: str
    varid: str
    catSequence: list[str]

class RuleGenerator:

    SectionSequence = ['section-def-cats', 'section-def-attrs',
                       'section-def-vars', 'section-def-lists',
                       'section-def-macros', 'section-rules']

    def __init__(self, sourceDB, targetDB, report, configMap):
        self.sourceDB = sourceDB
        self.targetDB = targetDB
        self.report = report
        self.configMap = configMap

        self.sourceHierarchy = Utils.getCategoryHierarchy(sourceDB)
        self.targetHierarchy = Utils.getCategoryHierarchy(targetDB)

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
        self.tagAndFeaturesToCategoryName: dict[tuple[str, frozenset, frozenset], str] = {}

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

    def GetCategory(self, category: str, source: bool = True,
                    target: bool = True) -> set[str]:
        ls = [category]
        if source:
            ls += self.sourceHierarchy.get(category, [])
        if target:
            ls += self.targetHierarchy.get(category, [])
        return set(ls)

    def GetCategoryName(self, category: str, features: set[tuple[str, str]],
                        affixes: set[tuple[str, str]]) -> str:
        if not features and not affixes:
            return self.tagToCategoryName[category]
        key = (category, frozenset(features), frozenset(affixes))
        if key in self.tagAndFeaturesToCategoryName:
            return self.tagAndFeaturesToCategoryName[key]

        pieces = ['c', category] + \
            sorted(v[1] for v in features) + \
            sorted(v[1] for v in affixes)
        name = self.GetAvailableID('_'.join(pieces))

        tag_list = [category, category+'.*']
        next_tag_list = []
        for seq in permutations(sorted(features)):
            append = ['']
            for label, value in seq:
                append = [f'{a}.{value}' for a in append] + \
                    [f'{a}.{value}.*' for a in append]
            next_tag_list += [t+a for t in tag_list for a in append]
        if next_tag_list:
            tag_list = next_tag_list
        # TODO: get tags for affixes

        elem = ET.SubElement(self.GetSection('section-def-cats'), 'def-cat',
                             n=name)
        for tg in tag_list:
            ET.SubElement(elem, 'cat-item', tags=tg)

        self.definedCategories[name] = [(None, t) for t in tag_list]
        self.tagAndFeaturesToCategoryName[key] = name
        return name

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
            # The block below allows multi-source macros to be reused,
            # but this causes some problems, so we're disabling it for now.
            # See #661
            '''
            if code := macro.get('c'):
                items = code.split()
                if len(items) > 3 and items[0] == 'FTM':
                    lookupKey = (items[2], tuple(items[3:]))
                    self.lemmaMacros[lookupKey] = MacroSpec(
                        macro.get('n'), items[1], items[3:])
            '''

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

        clean = start.replace(' ', '_')

        if clean not in self.usedIDs:
            self.usedIDs.add(clean)
            return clean

        n = 1
        while True:
            s = f'{clean}{n}'
            if s not in self.usedIDs:
                self.usedIDs.add(s)
                return s
            n += 1

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
                           comment: Optional[str] = None) -> str:
        for name, values in self.definedAttributes.items():
            if items <= values:
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

    def EnsureAttribute(self, spec: FeatureSpec) -> str:
        '''Return the name of the attribute corresponding to feature `label`
        for part of speech `category`, creating it if necessary.'''

        if (spec.category, spec.label) in self.featureToAttributeName:
            return self.featureToAttributeName[(spec.category, spec.label)]

        args = [self.report, self.configMap, spec.category, spec.label]
        if spec.isAffix:
            args[2] = self.GetCategory(spec.category)
            srcValues = Utils.getAffixGlossesForFeature(self.sourceDB, *args)
            trgValues = Utils.getAffixGlossesForFeature(self.targetDB, *args)
            values = set(Utils.underscores(l[0]) for l in srcValues + trgValues)
        else:
            srcValues = [(t, t) for t in Utils.getPossibleFeatureValues(
                self.sourceDB, spec.label)]
            trgValues = Utils.getLemmasForFeature(self.targetDB, *args)
            values = set(Utils.underscores(l[1]) for l in srcValues + trgValues)

        if spec.isAffix:
            name = f'a_{spec.category}_{spec.label}_slot'
        else:
            name = f'a_{spec.label}_feature'
        if not values:
            self.report.Error(f'Could not find any tags for feature {spec.label} of part-of-speech {spec.category}.')
        aid = self.AddSingleAttribute(name, values)
        self.featureToAttributeName[(spec.category, spec.label)] = aid
        return aid

    def AddVariable(self, name: str, comment: Optional[str] = None) -> None:
        '''Add a variable definition to <section-def-vars>, attempting
        to keep the section alphabetical.'''

        def GetIndex(section: ET.Element, name: str) -> int:
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

    def GetTags(self, spec: FeatureSpec, source: bool = False) -> set[tuple[str, str]]:
        '''Return a set of tuples where the first element is the tag that
        would appear in the stream and the second element is the feature
        value so that we can match it up with the tags for other categories.'''

        if source or spec.isSource:
            if spec.isAffix:
                ret = Utils.getAffixGlossesForFeature(
                    self.sourceDB, self.report, self.configMap,
                    self.GetCategory(spec.category, target=False), spec.label)
            else:
                ret = [(tag, tag) for tag in Utils.getPossibleFeatureValues(
                    self.sourceDB, spec.label)]
        else:
            if spec.isAffix:
                ret = Utils.getAffixGlossesForFeature(
                    self.targetDB, self.report, self.configMap,
                    self.GetCategory(spec.category, source=False), spec.label)
            else:
                # If we're getting lemma features, they will show up as their
                # values, so we discard the actual lemmas.
                ret = [(l[1], l[1]) for l in Utils.getLemmasForFeature(
                    self.targetDB, self.report, self.configMap,
                    spec.category, spec.label)]

        ret = [(Utils.underscores(a), Utils.underscores(b)) for a, b in ret]

        if spec.value:
            ret = [x for x in ret if x[1] == spec.value]

        return set(ret)

    def SameAffixTags(self, cat: str, label: str):
        '''Check whether the source and target projects have the same
        set of affixes for a particular feature.'''

        src = self.GetTags(FeatureSpec(cat, label, True, isSource=True))
        trg = self.GetTags(FeatureSpec(cat, label, True, isSource=False))

        return src == trg

    def GetAttributeMacro(self, srcSpec: FeatureSpec, trgSpec: FeatureSpec) -> Optional[MacroSpec]:
        '''Return the macro and variable names for converting between the
        category+attribute pairs `srcSpec` and `trgSpec`, creating the macro
        if necessary. If no conversion is needed and a simple <clip> can be
        used, then `(None, None)` will be returned.'''

        if (srcSpec, trgSpec) in self.attributeMacros:
            return self.attributeMacros[(srcSpec, trgSpec)]

        src = self.GetTags(srcSpec, source=True)
        trg = self.GetTags(trgSpec, source=False)

        def FindTag(srcFeat, fallback=None):
            nonlocal trg
            for trgTag, trgFeat in trg:
                if trgFeat == srcFeat:
                    return trgTag
            if fallback is not None:
                return fallback
            return f'{srcFeat}-NOTAG'

        def MakeWhenClause(element, varid, value):
            when = ET.SubElement(element, 'when')
            test = ET.SubElement(when, 'test')
            eq = ET.SubElement(test, 'equal')
            let = ET.SubElement(when, 'let')
            ET.SubElement(let, 'var', n=varid)
            ET.SubElement(let, ('lit-tag' if value else 'lit'), v=value)
            return eq

        if src == trg:
            if not srcSpec.default:
                self.attributeMacros[(srcSpec, trgSpec)] = None
                return None

            # If the target POS doesn't have an affix for the default
            # value, then we don't need a choose block and can just do
            # a plain clip.
            hasDefault = any(t[1] == srcSpec.default for t in trg)
            if not hasDefault:
                self.attributeMacros[(srcSpec, trgSpec)] = None
                return None

            # If there's a default value, we still need to check for the empty
            # case, but we can skip the rest of the conditional.

            macid = self.GetAvailableID(f'm_{srcSpec.xmlLabel}-to-{trgSpec.xmlLabel}')
            varid = self.GetAvailableID(f'v_{trgSpec.xmlLabel}')
            self.AddVariable(varid, f'Used by macro {macid}')
            macro = ET.SubElement(self.GetSection('section-def-macros'),
                                  'def-macro', n=macid, npar='1')
            let1 = ET.SubElement(macro, 'let')
            ET.SubElement(let1, 'var', n=varid)
            ET.SubElement(let1, 'clip', pos='1', side='tl',
                          part=self.EnsureAttribute(srcSpec))

            choose = ET.SubElement(macro, 'choose')
            eq = MakeWhenClause(choose, varid, FindTag(srcSpec.default))
            ET.SubElement(eq, 'var', n=varid)
            ET.SubElement(eq, 'lit', v='')

            spec = MacroSpec(macid, varid, [srcSpec.category])
            self.attributeMacros[(srcSpec, trgSpec)] = spec
            return spec

        macid = self.GetAvailableID(f'm_{srcSpec.xmlLabel}-to-{trgSpec.xmlLabel}')
        varid = self.GetAvailableID(f'v_{trgSpec.xmlLabel}')
        self.AddVariable(varid, f'Used by macro {macid}')
        macro = ET.SubElement(self.GetSection('section-def-macros'), 'def-macro',
                              n=macid, npar='1')

        macro.append(ET.Comment("Clear the variable to be sure we don't accidentally retain a prior value"))
        let1 = ET.SubElement(macro, 'let')
        ET.SubElement(let1, 'var', n=varid)
        ET.SubElement(let1, 'lit', v='')

        choose = ET.SubElement(macro, 'choose')
        for srcTag, srcFeat in src:
            if srcFeat == srcSpec.default:
                continue

            eq = MakeWhenClause(choose, varid, FindTag(srcFeat))
            ET.SubElement(eq, 'clip', pos='1', side='tl',
                          part=self.EnsureAttribute(srcSpec))
            ET.SubElement(eq, 'lit-tag', v=srcTag)

        otherwise = ET.SubElement(choose, 'otherwise')
        olet = ET.SubElement(otherwise, 'let')
        ET.SubElement(olet, 'var', n=varid)
        if srcSpec.default:
            val = FindTag(srcSpec.default, fallback='')
            ET.SubElement(olet, ('lit-tag' if val else 'lit'), v=val)
        else:
            ET.SubElement(olet, 'lit-tag', v=f'{trgSpec.label}-UNK')

        spec = MacroSpec(macid, varid, [srcSpec.category])
        self.attributeMacros[(srcSpec, trgSpec)] = spec
        return spec

    def GetMultiFeatureMacro(self, destCategory: str, isLemma: bool, sources: list[FeatureSpec]) -> MacroSpec:
        '''Find or generate the appropriate macro for changing the lemma of
        a word with part of speech `destCategory` based on a set of agreement
        features (`sources`). Return the macro name, the variable name, and
        the order of the arguments to the macro by part-of-speech tag.'''

        # TODO: most of the variable names in this function are from when
        # it was solely for lemmas. They should probably be updated.

        catSequence = sorted(set([s.category for s in sources if not s.value]))
        lookupKey = (destCategory, tuple(catSequence))
        if lookupKey in self.lemmaMacros:
            return self.lemmaMacros[lookupKey]

        macType = 'lemma' if isLemma else 'affix'
        label = f'{destCategory}_{macType}_from_{"-".join(catSequence)}'
        macid = self.GetAvailableID('m_'+label)
        varid = self.GetAvailableID('v_'+label)
        self.AddVariable(varid, f'Used by macro {macid}')
        code = ' '.join([destCategory] + catSequence)
        macro = ET.SubElement(self.GetSection('section-def-macros'), 'def-macro',
                              n=macid, npar=str(len(catSequence)),
                              c=f'FTM {varid} {code}')

        for n, cat in enumerate(catSequence, 1):
            macro.append(ET.Comment(f'Item {n} is part-of-speech {cat}.'))

        def SetVar(parent, value):
            nonlocal varid, isLemma
            let = ET.SubElement(parent, 'let')
            ET.SubElement(let, 'var', n=varid)
            ET.SubElement(let, 'lit' if (isLemma or not value) else 'lit-tag',
                          v=value)

        macro.append(ET.Comment("Clear the variable to be sure we don't accidentally retain a prior value"))
        SetVar(macro, '')

        ranked = False
        sourceList = sources
        if all(s.ranking for s in sources):
            ranked = True
            sourceList = sorted(sources, key=lambda s: s.ranking)

        labelSeq = [s.label for s in sources]
        locations = [(macro, None, [])]
        for source in sourceList:
            if source.category in catSequence:
                clipPos = str(catSequence.index(source.category)+1)
            else:
                # anything not in catSequence should have non-empty value,
                # so we shouldn't ever insert clipPos anywhere
                clipPos = 'ERROR'
            tags = sorted(self.GetTags(source, source=(source.isAffix)))
            if isLemma:
                allLemmas = Utils.getLemmasForFeature(
                    self.targetDB, self.report, self.configMap, destCategory,
                    source.label)
            else:
                allLemmas = self.GetTags(FeatureSpec(destCategory, source.label,
                                                     True))

            newLocations = []

            if source.value:
                allLemmas = [l for l in allLemmas if l[1] == source.value]
                for elem, possibleLemmas, path in locations:
                    lemmas = allLemmas
                    if possibleLemmas is not None:
                        lemmas = [l for l in allLemmas if l[0] in possibleLemmas]
                    newLocations.append((elem, set([l[0] for l in lemmas]),
                                         path+[source.value]))
                locations = newLocations
                continue

            for elem, possibleLemmas, path in locations:
                lemmas = allLemmas
                if possibleLemmas is not None:
                    lemmas = [l for l in allLemmas if l[0] in possibleLemmas]

                if not lemmas and source.default:
                    newPossible = set([l for l in possibleLemmas
                                       if all(a[0] != l for a in allLemmas)])
                    if newPossible:
                        newLocations.append((elem, newPossible,
                                             path+[source.default]))
                        continue

                if not lemmas or not tags:
                    error = macType+'-for-'+'-'.join(path)
                    if not ranked or not possibleLemmas:
                        SetVar(elem, 'no-'+error)
                    elif len(possibleLemmas) > 1:
                        SetVar(elem, 'multiple'+error)
                    else:
                        SetVar(elem, list(possibleLemmas)[0])
                    continue

                given = ''
                if path:
                    specs = [f'{label} = {value}' for label, value in zip(labelSeq, path)]
                    given = f' given {", ".join(specs)}'
                elem.append(ET.Comment(f'Narrow the set of possible values based on {source.label} ({", ".join(sorted(t[1] for t in tags))}){given}.'))
                choose = ET.SubElement(elem, 'choose')
                for tag, feature in tags:
                    if feature == source.default:
                        # Handle this in the <otherwise> block
                        continue

                    choose.append(ET.Comment(f'Set {varid} based on {source.label} = {feature}.'))
                    when = ET.SubElement(choose, 'when')
                    test = ET.SubElement(when, 'test')
                    eq = ET.SubElement(test, 'equal')
                    side = 'tl'
                    if source.isSource and not source.isAffix:
                        side = 'sl'
                    ET.SubElement(
                        eq, 'clip', pos=clipPos, side=side,
                        part=self.EnsureAttribute(source))
                    ET.SubElement(eq, 'lit-tag', v=tag)
                    nextLemmas = set(l[0] for l in lemmas if l[1] == feature)
                    newLocations.append((when, nextLemmas, path+[feature]))

                otherwise = ET.SubElement(choose, 'otherwise')
                if source.default:
                    nextLemmas = set(l[0] for l in lemmas if l[1] == source.default)
                    newLocations.append((otherwise, nextLemmas or None, path+[source.default]))
                else:
                    SetVar(otherwise, f'no-{macType}-for-'+'-'.join(path))

            locations = newLocations

        for elem, possibleLemmas, path in locations:
            error = f'{macType}-for-' + '-'.join(path)
            if possibleLemmas is None:
                value = ''
            elif len(possibleLemmas) == 0:
                value = 'no-'+error
            elif len(possibleLemmas) == 1:
                value = list(possibleLemmas)[0]
            else:
                lemmas = ', '.join(sorted(possibleLemmas))
                elem.append(ET.Comment(f'Possible values with this combination of tags: {lemmas}'))
                value = 'multiple-'+error
            SetVar(elem, value)

        spec = MacroSpec(macid, varid, catSequence)
        self.lemmaMacros[lookupKey] = spec
        return spec

    def ProcessRule(self, rule: ET.Element, skip: Optional[set[str]] = None) -> bool:
        '''Convert a Rule Assistant <Rule> node `rule` to an Apertium <rule>
        node and append it to the current XML tree. Return whether a rule
        was created. Skip any words whose id field is in `skip`.'''

        ruleName = rule.get('name')

        sourceWords = []
        sourceIDs = set()
        for word in rule.findall('.//Source//Word'):
            wid = word.get('id')
            if wid in sourceIDs:
                self.report.Error(f'Multiple source words have ID {wid} in rule "{ruleName}".')
                return False
            sourceIDs.add(wid)
            cat = word.get('category')
            if cat is None:
                self.report.Error(f'Source word {wid} in rule "{ruleName}" has no category.')
                return False
            features = set()
            affixes = set()
            for feat in word.findall('./Features/Feature'):
                if value := feat.get('value'):
                    features.add((feat.get('label'), value))
            for feat in word.findall('.//Affix/Feature'):
                if value := feat.get('value'):
                    affixes.add((feat.get('label'), value))
            sourceWords.append((wid, cat, features, affixes))

        if rule.find(".//Target//Word[@head='yes']") is None:
            self.report.Error(f'No target word has been set as head in rule "{ruleName}".')
            return False

        if skip is not None:
            ruleName += ': '
            ruleName += ' '.join([w[1] for w in sourceWords if w[0] not in skip])
        if ruleName in self.ruleNames:
            index = 1
            while True:
                altName = f'{ruleName} ({index})'
                if altName not in self.ruleNames:
                    break
                index += 1
            self.report.Info(f'Rule name "{ruleName}" already exists in the rule file. Renaming added rule to "{altName}".')
            ruleName = altName

        ruleEl = ET.SubElement(self.GetSection('section-rules'), 'rule',
                               comment=ruleName)
        self.ruleNames.add(ruleName)

        wordCats = {}
        wordLocation = {}
        patternEl = ET.SubElement(ruleEl, 'pattern')
        index = 0
        for wid, cat, features, affixes in sourceWords:
            if skip and wid in skip:
                continue
            index += 1
            name = self.GetCategoryName(cat, features, affixes)
            ET.SubElement(patternEl, 'pattern-item', n=name)
            wordLocation[wid] = str(index)
            wordCats[str(index)] = cat

        actionEl = ET.SubElement(ruleEl, 'action')

        outEl = ET.Element('out')

        usedMacros = set()

        matches = defaultdict(list)

        # If there are match groups on the source side, list them first
        # so that their positions override the target match group positions.
        for word in rule.findall('.//Source//Word'):
            wid = word.get('id')
            if skip and wid in skip:
                continue
            pos = wordLocation.get(wid)
            for feat in word.findall('./Features/Feature'):
                matches[(feat.get('label'), feat.get('match'))].append(
                    (pos, True, False, feat.get('unmarked_default'), True))
            for feat in word.findall('.//Affix//Feature'):
                matches[(feat.get('label'), feat.get('match'))].append(
                    (pos, True, True, feat.get('unmarked_default'), True))

        # Now record the match groups on the target side, tracking whether
        # the word they appear on is marked as head or not, since we want
        # information to flow from head to dependent by default.
        for word in rule.findall('.//Target//Word'):
            head = (word.get('head') == 'yes')
            wid = word.get('id')
            if skip and wid in skip:
                continue
            pos = wordLocation.get(wid)
            for feat in word.findall('./Features/Feature'):
                matches[(feat.get('label'), feat.get('match'))].append(
                    (pos, head, False, feat.get('unmarked_default'), False))
            for feat in word.findall('.//Affix//Feature'):
                matches[(feat.get('label'), feat.get('match'))].append(
                    (pos, head, True, feat.get('unmarked_default'), False))

        # For each combination of feature and match set, find the best source,
        # where the head word is preferred, if available, and otherwise we
        # take the rightmost word that has it as a stem feature rather than
        # an affix (rightmost not for any theoretical reason, but simply
        # because that was the easiest way to structure the loop).
        # If no such source is found, report an error.
        featureSources = {}
        for (label, match), items in matches.items():
            if match is None:
                continue
            cur = None
            for wid, head, affix, default, isSource in items:
                if head:
                    cur = (wid, affix, default, isSource)
                    break
                elif not affix and cur is None:
                    cur = (wid, affix, default, isSource)
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
                cat = word.get('category')
                if not cat:
                    self.report.Error(f'Missing category for inserted word {wid} in rule {ruleName}.')
                    self.GetSection('section-rules').remove(ruleEl)
                    return False
            else:
                cat = wordCats[pos]

            # If the stem features have a source that isn't this word,
            # we want to use a macro to check that we have the right lemma.
            lemmaTags = []
            lemmaLocs = {}
            for feature in word.findall('./Features/Feature'):
                label = feature.get('label')
                match = feature.get('match')
                value = feature.get('value')
                tgtDefault = feature.get('unmarked_default')
                ranking = feature.get('ranking')
                if ranking:
                    ranking = int(ranking)
                if not value:
                    apos, isAffix, srcDefault, isSource = featureSources.get(
                        (label, match), (pos, False, None, False))
                else:
                    apos, isAffix, srcDefault, isSource = pos, False, None, False
                srcCat = wordCats.get(apos)
                if apos is None:
                    if value:
                        srcCat = cat
                    else:
                        self.report.Error(f'Missing source for feature {label} on inserted word {wid} in rule {ruleName}.')
                        self.GetSection('section-rules').remove(ruleEl)
                        return False
                lemmaTags.append(FeatureSpec(srcCat, label, isAffix,
                                             value=value, ranking=ranking,
                                             default=(tgtDefault or srcDefault),
                                             isSource=isSource))
                if apos is not None:
                    lemmaLocs[srcCat] = apos
            shouldUseLemmaMacro = lemmaTags and lemmaLocs != {cat:pos}

            if pos is None and not shouldUseLemmaMacro:
                self.report.Error(f'Unable to generate lemma for inserted word {wid} in rule {ruleName}.')
                self.GetSection('section-rules').reomve(ruleEl)
                return False

            # TODO: check that it's not a proper noun
            if index == 0 and (pos != '1' or shouldUseLemmaMacro):
                lemCase = ET.SubElement(lu, 'get-case-from', pos='1')
            elif index > 0 and pos == '1' and index < len(sourceWords):
                # The last condition applies when we have an inserted word,
                # and it might result in outputting a capitalized word in
                # non-initial position. I'm not entirely sure what to do
                # about this though.
                lemCase = ET.SubElement(lu, 'get-case-from', pos=str(index+1))
            else:
                lemCase = lu

            if shouldUseLemmaMacro:
                spec = self.GetMultiFeatureMacro(cat, True, lemmaTags)
                if spec.macid not in usedMacros:
                    actionEl.append(ET.Comment(f'Determine the appropriate lemma for {cat} and store it in a variable named {spec.varid}.'))
                    callmac = ET.SubElement(actionEl, 'call-macro', n=spec.macid)
                    for srcCat in spec.catSequence:
                        ET.SubElement(callmac, 'with-param',
                                      pos=lemmaLocs[srcCat])
                    usedMacros.add(spec.macid)
                ET.SubElement(lemCase, 'var', n=spec.varid)
            else:
                ET.SubElement(lemCase, 'clip', pos=pos, side='tl', part='lem')

            if pos is None:
                ET.SubElement(lu, 'lit-tag', v=cat)
            else:
                ET.SubElement(
                    lu, 'clip', pos=pos, side='tl', part=self.categoryAttribute,
                )

            # Force prefixes to be before suffixes
            prefixFeatures = []
            suffixFeatures = []
            prefixes = []
            suffixes = []
            for affix in word.findall('.//Affix'):
                prefix = (affix.get('type', 'suffix') == 'prefix')
                features = []
                for feature in affix.findall('.//Feature'):
                    label = feature.get('label')
                    match = feature.get('match')
                    value = feature.get('value')
                    default = feature.get('unmarked_default')
                    ranking = feature.get('ranking')
                    if ranking:
                        ranking = int(ranking)
                    features.append((label, match, value, default, ranking))
                if not features:
                    continue
                if prefix:
                    prefixes.append(features)
                else:
                    suffixes.append(features)

            for affix in prefixes + suffixes:

                if len(affix) > 1:
                    specList = []
                    catLoc = {}
                    for label, match, value, tgtDefault, ranking in affix:
                        apos, isAffix, srcDefault, isSource = featureSources.get(
                            (label, match), (pos, True, None, False))
                        srcCat = wordCats.get(apos)
                        if apos is None:
                            if value:
                                srcCat = cat
                            else:
                                self.report.Error('Unable to find source for feature {label} on word {wid} in rule {ruleName}.')
                                self.GetSection('section-rules').reomve(ruleEl)
                                return False
                        default = tgtDefault or srcDefault
                        specList.append(FeatureSpec(srcCat, label,
                                                    isAffix, value=value,
                                                    default=default,
                                                    isSource=isSource,
                                                    ranking=ranking))
                        catLoc[srcCat] = apos
                    spec = self.GetMultiFeatureMacro(cat, False, specList)
                    if spec.macid not in usedMacros:
                        actionEl.append(ET.Comment(f'Determine the appropriate affix for {cat} and store it in a variable named {spec.varid}.'))
                        callmac = ET.SubElement(actionEl, 'call-macro',
                                                n=spec.macid)
                        for srcCat in spec.catSequence:
                            ET.SubElement(callmac, 'with-param',
                                          pos=catLoc[srcCat])
                        usedMacros.add(spec.macid)
                    ET.SubElement(lu, 'var', n=spec.varid)
                    continue

                label, match, value, tgtDefault, ranking = affix[0]

                if value:
                    tags = self.GetTags(FeatureSpec(wordCats[pos], label, True,
                                                    value=value))
                    if tags:
                        ET.SubElement(lu, 'lit-tag', v=sorted(tags)[0][0])
                    else:
                        self.report.Error(f'No tag found for value {value} of feature {label} in rule "{ruleName}".')
                        self.GetSection('section-rules').remove(ruleEl)
                        return False
                    continue

                apos, isAffix, srcDefault, isSource = featureSources.get(
                    (label, match), (pos, True, None, False))
                if apos is None:
                    self.report.Error('Unable to find source for feature {label} on word {wid} in rule {ruleName}.')
                    self.GetSection('section-rules').reomve(ruleEl)
                    return False
                default = tgtDefault or srcDefault
                if apos != pos or not self.SameAffixTags(wordCats[apos], label):
                    spec = self.GetAttributeMacro(
                        FeatureSpec(wordCats[apos], label, isAffix,
                                    default=default, isSource=isSource),
                        FeatureSpec(cat, label, True))
                    if spec is not None:
                        if spec.macid not in usedMacros:
                            actionEl.append(ET.Comment(f'Determine the appropriate {label} tag for {cat} and store it in a variable named {spec.varid}.'))
                            callmac = ET.SubElement(actionEl, 'call-macro',
                                                    n=spec.macid)
                            ET.SubElement(callmac, 'with-param', pos=apos)
                            usedMacros.add(spec.macid)
                        ET.SubElement(lu, 'var', n=spec.varid)
                        continue
                attr = self.EnsureAttribute(FeatureSpec(cat, label, True))
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

        self.categoryAttribute = 'a_gram_cat'
        if self.categoryAttribute not in self.definedAttributes:
            # Hypothetically, someone could have named a variable or macro
            # "a_gram_cat", and we don't want to conflict with that.
            self.categoryAttribute = self.AddSingleAttribute(
                'a_gram_cat', set(self.tagToCategoryName.keys()),
                comment='Part-of-speech tags used in the rules')
        catElem = self.root.find(f".//def-attr[@n='{self.categoryAttribute}']")
        for tag in self.tagToCategoryName:
            if tag not in self.definedAttributes[self.categoryAttribute]:
                ET.SubElement(catElem, 'attr-item', tags=tag)
                self.definedAttributes[self.categoryAttribute].add(tag)

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

        # The transfer DTD doesn't allow sections to be empty,
        # so simply don't include them in that case.
        for name in RuleGenerator.SectionSequence:
            elem = self.GetSection(name)
            if len(elem) == 0:
                self.root.remove(elem)

        with open(fileName, 'wb') as fout:
            fout.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf-8'))
            fout.write('<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN" "transfer.dtd">\n'.encode('utf-8'))
            ET.indent(self.root)
            fout.write(ET.tostring(self.root, encoding='utf-8'))

# Wrapper function which calls the necessary logic to write rules to the Aperitum file
def CreateRules(sourceDB, targetDB, report, configMap, ruleAssistantFile, transferRulePath, ruleNumber):

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

    generator = RuleGenerator(sourceDB, targetDB, report, configMap)

    if os.path.exists(transferRulePath):

        datetimeStr = re.sub(':', '-', datetime.datetime.now().isoformat(sep=' ', timespec='seconds'))
        backupPath = f'{transferRulePath}.{datetimeStr}.bak'
        report.Info(f'Copying prior version of transfer rules to {backupPath}.')
        shutil.copy(transferRulePath, backupPath)
        generator.ProcessExistingTransferFile(transferRulePath)

    generator.ProcessAssistantFile(ruleAssistantFile, ruleNumber)

    generator.WriteTransferFile(transferRulePath)

    return True
