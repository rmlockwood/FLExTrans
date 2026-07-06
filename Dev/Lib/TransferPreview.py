#
#   TransferPreview
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16.3 - 7/6/26 - Ron Lockwood
#    Diff highlighting is now confined to the side-by-side comparison (a new compare flag); the single-rule create/explain views render plain like XXE instead of being flagged wholesale
#    as "added" (which had tinted the whole rule green). Restyled to match XXE: Arial 16px labels/chips, the extra per-item indents from transfer.css (pattern-item .4in, attr/list-item
#    .2in), the side value coloured like the XXE combo box (red for sl, ochre for tl), and a pale-yellow (#ffffdd) comment box with grey serif-monospace text (no "//" prefix). An empty
#    value (e.g. <lit v=""/>) now renders as an empty coloured box rather than collapsing to nothing.
#
#   Version 3.16.4 - 7/6/26 - Ron Lockwood
#    The side-by-side comparison now aligns children with difflib instead of strict position, so an inserted or deleted node (e.g. the authorship/description comments prepended to a
#    modified rule, or one added clip) marks only itself rather than shifting every following row and lighting up the whole rule.
#
#   Version 3.16.2 - 7/5/26 - Ron Lockwood
#    Added renderExplanationHtml for the new explain mode: the rule rendered XXE-style on the left, the AI's plain-text explanation (escaped, paragraphs preserved) on the right.
#
#   Version 3.16.1 - 7/3/26 - Ron Lockwood
#    Chip/box colours now come from the derived preview_spec JSON (parsed from the XXE stylesheet's @property-value declarations) instead of only the hard-coded values in
#    transfer_preview.css, so editing a colour in the XXE CSS flows into the preview.
#
#   Version 3.16 - 7/2/26 - Ron Lockwood
#    Prototype. Render an Apertium transfer <rule> (and supporting definitions) as read-only styled HTML for the "Work on Rules with AI" preview. Mirrors the XXE stylesheet's palette
#    and labels via transfer_preview.css. Produces a single render (for creating a rule) or a side-by-side before/after comparison (for modifying one) with best-effort diff highlighting.
#    No raw markup is ever shown to the user - only the rendered result goes into a QWebEngineView.

import os
import json
import html
import difflib
import xml.etree.ElementTree as ET

# realpath so this resolves through a per-file symlink (dev deploy) to the real Lib folder where transfer_preview.css actually sits.
CSS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'transfer_preview.css')

# Human-friendly value for the side attribute, matching the XXE combo-box labels.
SIDE_LABELS = {'sl': 'source lang.', 'tl': 'target lang.'}

# Per-element display spec: (labelText, [(attrName, attrLabel, colorClass), ...]). labelText is the element's ":before" text; each attribute is rendered as a labelled coloured chip.
# Colours/labels are lifted from transfer.css. An element not listed falls back to showing its tag name and all its attributes generically.
SPEC = {
    'action':             ('action: ', []),
    'and':                ('and: ', []),
    'or':                 ('or: ', []),
    'not':                ('not: ', []),
    'choose':             ('choose: ', []),
    'when':               ('when: ', []),
    'otherwise':          ('otherwise: ', []),
    'test':               ('test: ', []),
    'equal':              ('equal: ', []),
    'pattern':            ('pattern: ', []),
    'pattern-item':       ('item: ', [('n', '', 'c-cat')]),
    'let':                ('let: ', []),
    'var':                ('variable: ', [('n', '', 'c-var')]),
    'clip':               ('clip - ', [('pos', 'item: ', 'c-pos'), ('side', 'side: ', 'c-plain'), ('part', 'part: ', 'c-attr')]),
    'lit':                ('literal string: ', [('v', '', 'c-lit')]),
    'lit-tag':            ('literal tag: ', [('v', '', 'c-littag')]),
    'out':                ('output: ', []),
    'lu':                 ('lexical unit: ', []),
    'mlu':                ('multi-word: ', []),
    'b':                  ('blank space', []),
    'call-macro':         ('call macro: ', [('n', '', 'c-macro')]),
    'with-param':         ('with item: ', [('pos', '', 'c-pos')]),
    'rule':               ('rule: ', [('comment', '', 'c-rule')]),
    'cat-item':           ('tags: ', [('tags', '', 'c-chunk'), ('lemma', 'lemma: ', 'c-chunk')]),
    'attr-item':          ('tags: ', [('tags', '', 'c-chunk')]),
    'def-cat':            ('category: ', [('n', '', 'c-cat')]),
    'def-attr':           ('attribute: ', [('n', '', 'c-attr')]),
    'def-var':            ('variable: ', [('n', '', 'c-var')]),
    'def-list':           ('list: ', [('n', '', 'c-list')]),
    'list':               ('list: ', [('n', '', 'c-list')]),
    'list-item':          ('item: ', [('v', '', 'c-lit')]),
    'def-macro':          ('macro: ', [('n', '', 'c-macro'), ('npar', 'number of items = ', 'c-pos')]),
    'chunk':              ('chunk - name: ', [('name', '', 'c-chunk'), ('namefrom', 'get name from variable: ', 'c-var')]),
    'tag':                ('tag: ', []),
    'get-case-from':      ('get case from item: ', [('pos', '', 'c-pos')]),
    'case-of':            ('case of - ', [('pos', 'item: ', 'c-pos'), ('side', 'side: ', 'c-plain'), ('part', 'part: ', 'c-attr')]),
    'modify-case':        ('modify case: ', []),
    'append':            ('append to: ', [('n', '', 'c-var')]),
    'concat':             ('concat: ', []),
    'begins-with':        ('begins with: ', []),
    'ends-with':          ('ends with: ', []),
    'begins-with-list':   ('begins with something in list: ', []),
    'ends-with-list':     ('ends with something in list: ', []),
    'contains-substring': ('contains substring: ', []),
    'in':                 ('in list: ', []),
}

LIB_DIR = os.path.dirname(os.path.realpath(__file__))
_specCache = {}

def loadSpec(lang: str) -> dict:
    '''Load the per-language display spec (labels + colours) that derive_preview_specs.py generated from transfer.css. Falls back to English, then to the built-in SPEC if no file is found,
    so the preview always renders even before the derivation has been run.'''

    lang = (lang or 'en').lower()

    if lang in _specCache:
        return _specCache[lang]

    for candidate in (lang, 'en'):

        path = os.path.join(LIB_DIR, 'preview_spec_{lang}.json'.format(lang=candidate))
        if os.path.isfile(path):
            _specCache[lang] = json.load(open(path, encoding='utf-8'))
            return _specCache[lang]

    _specCache[lang] = SPEC
    return SPEC

def loadCss() -> str:
    '''Read the reskin CSS so it can be inlined into the document.'''

    return open(CSS_PATH, encoding='utf-8').read()

def isComment(elem) -> bool:
    '''ET represents comment nodes with a callable tag; detect them.'''

    return callable(elem.tag)

def childKey(elem):
    '''The key the comparison uses to line up an element against its counterpart: its tag (so like elements match and an attribute-only change still pairs and is flagged), or a single
    shared key for every comment (so a comment lines up with a comment - e.g. one authorship stamp against another - rather than against a real element).'''

    return '#comment' if isComment(elem) else elem.tag

def renderChip(value: str, colorClass: str) -> str:
    '''Render one attribute value. Most values are coloured chips (a bordered box); the "plain" classes (c-plain and the c-side-* side colours) are shown as plain coloured text with no box.'''

    shown = html.escape(value)

    if colorClass == 'c-plain' or colorClass.startswith('c-side'):
        return '<span class="{cls}">{val}</span>'.format(cls=colorClass, val=shown)

    # An empty value (e.g. <lit v=""/>, the empty string used to clear an attribute) still gets a visible coloured box: a non-breaking space gives it content, and the chip's min-width
    # keeps it from collapsing, so an empty literal reads as an (empty-valued) box rather than nothing.
    return '<span class="chip {cls}">{val}</span>'.format(cls=colorClass, val=shown or '&nbsp;')

def renderRowLine(elem: ET.Element, spec: dict) -> str:
    '''Render an element's header row: its label plus its displayed attributes, using the given per-language display spec.'''

    entry = spec.get(elem.tag)

    if entry is None:
        # Fallback: show the tag name and every attribute generically.
        pieces = ['<span class="label">' + html.escape(elem.tag) + ': </span>']
        for name, value in elem.attrib.items():
            pieces.append('<span class="attrlabel">' + html.escape(name) + ': </span>' + renderChip(value, 'c-chunk'))
        return '<span class="rowline">' + ''.join(pieces) + '</span>'

    label, attrSpecs = entry
    pieces = ['<span class="label">' + html.escape(label) + '</span>']

    for name, attrLabel, colorClass in attrSpecs:

        if name not in elem.attrib:
            continue

        value = elem.attrib[name]

        if name == 'side':

            # Colour the side value the way the master XXE stylesheet does: red for source language (sl), ochre for target language (tl).
            colorClass = 'c-side-sl' if value == 'sl' else 'c-side-tl'
            value = SIDE_LABELS.get(value, value)

        if attrLabel:
            pieces.append('<span class="attrlabel">' + html.escape(attrLabel) + '</span>')

        pieces.append(renderChip(value, colorClass))

    return '<span class="rowline">' + ''.join(pieces) + '</span>'

def diffClass(elem: ET.Element, other) -> str:
    '''Diff class for an element vs. its positional counterpart: "changed" if the tag or attributes differ, else "".'''

    if other is None:
        return ''

    if isComment(elem) or isComment(other):
        return '' if (isComment(elem) and isComment(other) and (elem.text or '') == (other.text or '')) else 'changed'

    if elem.tag != other.tag or elem.attrib != other.attrib:
        return 'changed'

    return ''

def elementToHtml(elem, other=None, side: str = 'after', forced: str = '', spec=None, compare: bool = False) -> str:
    '''Recursively render an element to HTML.

    Diff highlighting only happens when `compare` is True (the side-by-side modify view). In the single-rule create/explain views `compare` is False and no added/changed/removed classes
    are emitted, so the rule renders plain (like XXE) rather than being flagged wholesale as "added". `other` is the positional counterpart in the compared tree; `side` is which pane we
    are rendering ("before"/"after") so a child with no counterpart is marked "removed" on the before side and "added" on the after side; `forced` propagates that marker down a subtree.'''

    if spec is None:
        spec = SPEC

    if isComment(elem):
        text = (elem.text or '').strip()
        cls = (forced or diffClass(elem, other)) if compare else ''
        classAttr = 'el comment' + ((' ' + cls) if cls else '')
        return '<div class="' + classAttr + '"><span class="rowline">' + html.escape(text) + '</span></div>'

    cls = (forced or diffClass(elem, other)) if compare else ''
    classAttr = 'el ' + elem.tag + ((' ' + cls) if cls else '')

    out = ['<div class="' + classAttr + '">', renderRowLine(elem, spec)]

    children = [c for c in elem]

    if children:

        out.append('<div class="children">')

        if not compare:

            # Single-rule render: no counterpart, no diff marking.
            for child in children:
                out.append(elementToHtml(child, None, side, '', spec, compare))

        elif forced:

            # This whole subtree is added/removed, so every descendant carries the same marker and has no counterpart.
            for child in children:
                out.append(elementToHtml(child, forced=forced, side=side, spec=spec, compare=compare))

        else:

            # Align this element's children with the counterpart's, matching by kind/tag (difflib) so an inserted or deleted child - e.g. the authorship/description comments prepended
            # to a modified rule, or an added clip - marks only itself, instead of shifting every following row and lighting up the whole rule. Matched children recurse (so an attribute
            # change is caught by diffClass); a child with no counterpart is "added" on the after pane and "removed" on the before pane.
            otherChildren = [c for c in other] if other is not None else []
            unmatched = 'added' if side == 'after' else 'removed'
            opcodes = difflib.SequenceMatcher(None, [childKey(c) for c in children], [childKey(c) for c in otherChildren]).get_opcodes()

            for op, i1, i2, j1, j2 in opcodes:

                if op == 'equal':

                    for k in range(i2 - i1):
                        out.append(elementToHtml(children[i1 + k], otherChildren[j1 + k], side, '', spec, compare))

                elif op == 'replace':

                    # Pair the overlap positionally so a like-for-like change recurses and diffClass flags it; any surplus on this side has no counterpart.
                    paired = min(i2 - i1, j2 - j1)

                    for k in range(paired):
                        out.append(elementToHtml(children[i1 + k], otherChildren[j1 + k], side, '', spec, compare))

                    for k in range(i1 + paired, i2):
                        out.append(elementToHtml(children[k], forced=unmatched, side=side, spec=spec, compare=compare))

                elif op == 'delete':

                    # Children present on this side but not the counterpart.
                    for k in range(i1, i2):
                        out.append(elementToHtml(children[k], forced=unmatched, side=side, spec=spec, compare=compare))

                # 'insert' means children only in the counterpart; they render in that pane, not this one.

        out.append('</div>')

    out.append('</div>')
    return ''.join(out)

def parseFragment(xmlText: str):
    '''Parse a rule/definition fragment, preserving comments.'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.fromstring(xmlText, parser=parser)

def colorsToCss(colors) -> str:
    '''Turn the spec's "_colors" map (chip class -> hex, derived from the XXE stylesheet by derive_preview_specs.py) into CSS rules. These come after transfer_preview.css in the
    document so they override its hard-coded fallback colours; an empty/missing map leaves the fallbacks in force.'''

    if not colors:
        return ''

    return '\n'.join('.{cls} {{ background: {hexColor}; }}'.format(cls=cls, hexColor=colors[cls]) for cls in sorted(colors))

def wrapDocument(bodyHtml: str, colors=None) -> str:
    '''Wrap rendered body HTML in a full document with the inlined CSS (plus the derived chip-colour overrides).'''

    return ('<!DOCTYPE html><html><head><meta charset="utf-8"><style>\n'
            + loadCss() + '\n' + colorsToCss(colors)
            + '\n</style></head><body>' + bodyHtml + '</body></html>')

def renderRuleHtml(ruleXml: str, newDefs=None, lang: str = 'en') -> str:
    '''Render a single rule (plus any new definitions) - used for the "create" preview. `lang` selects the label language. Returns a complete HTML document.'''

    spec = loadSpec(lang)
    body = []

    if newDefs:

        body.append('<div class="legend">New definitions to be added:</div>')

        for defText in newDefs:
            body.append(elementToHtml(parseFragment(defText), spec=spec))

    body.append(elementToHtml(parseFragment(ruleXml), spec=spec))
    return wrapDocument(''.join(body), spec.get('_colors'))

def renderExplanationHtml(ruleXml: str, explanationText: str, lang: str = 'en') -> str:
    '''Render the rule (styled like XXE) on the left and the AI's plain-text explanation on the right - used for the "explain" preview. The explanation is escaped and its blank-line
    breaks become paragraphs, so no raw markup is ever shown. Returns a complete HTML document.'''

    spec = loadSpec(lang)

    paragraphs = ''.join('<p>' + html.escape(par.strip()).replace('\n', '<br>') + '</p>' for par in explanationText.split('\n\n') if par.strip())

    left = '<div class="pane">' + elementToHtml(parseFragment(ruleXml), spec=spec) + '</div>'
    right = '<div class="pane explanation">' + paragraphs + '</div>'

    return wrapDocument('<div class="compare">' + left + right + '</div>', spec.get('_colors'))

def renderComparisonHtml(beforeXml: str, afterXml: str, lang: str = 'en') -> str:
    '''Render before/after side-by-side - used for the "modify" preview. `lang` selects the label language. Diff highlighting is best-effort (positional); the panes are always readable even
    if the highlighting is imperfect.'''

    spec = loadSpec(lang)
    before = parseFragment(beforeXml)
    after = parseFragment(afterXml)

    legend = ('<div class="legend">'
              '<span class="sw" style="background:#F7CAC9"></span>removed / changed on the left'
              '<span class="sw" style="background:#CFF5D1"></span>added on the right'
              '<span class="sw" style="background:#FFF3B0"></span>changed'
              '</div>')

    left = '<div class="pane"><h3>Before</h3>' + elementToHtml(before, after, side='before', spec=spec, compare=True) + '</div>'
    right = '<div class="pane"><h3>After</h3>' + elementToHtml(after, before, side='after', spec=spec, compare=True) + '</div>'

    return wrapDocument(legend + '<div class="compare">' + left + right + '</div>', spec.get('_colors'))
