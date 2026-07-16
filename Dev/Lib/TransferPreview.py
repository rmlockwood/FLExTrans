#
#   TransferPreview
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16.10 - 7/16/26 - Ron Lockwood
#    The explanation preview now switches its pane to right-to-left layout when the returned explanation text contains RTL characters, so Arabic/Hebrew content reads naturally in the explain pane.
#
#   Version 3.16.9 - 7/16/26 - Ron Lockwood
#    Which elements get a plus/minus collapser (the XXE minus-box/plus-box icons, embedded as data URIs) now comes from transfer.css: derive_preview_specs records which elements carry a
#    collapser() there ("_collapsible" in the spec), and the preview folds exactly those - except the single top-level rule/macro, which there is nothing to fold away from. Vertical indent
#    guides are a separate, preview-only set (the lengthy logic blocks choose/when/otherwise/test/out/and/or/not), independent of collapsibility. The caseless attribute renders as a disabled
#    checkbox with the stylesheet's localized label (e.g. "case insensitive"), shown on the comparison elements that support it and checked when caseless="yes" (a captured check-box() field).
#
#   Version 3.16.8 - 7/16/26 - Ron Lockwood
#    The explanation's Markdown is now rendered by the Python-Markdown package (new Markdown entry in the installer requirements), HTML-escaped
#    first so markup from the model can never render as live elements; tables and fenced code blocks now render too, with matching styles added to transfer_preview.css. In the two-pane
#    views (rule preview, comparison, explanation) the panes now scroll independently (body.split layout) so the explanation or the modified rule stays in view while scrolling the left rule.
#    The "changed" diff highlight is orange instead of yellow, since pale yellow is the comment-box background. loadSpec/loadCss now close their files (fixes a ResourceWarning in unit tests).
#
#   Version 3.16.7 - 7/10/26 - Ron Lockwood
#    transfer_preview.css moved to the Lib/css subfolder (with the Rule Assistant stylesheets); CSS_PATH now points there.
#
#   Version 3.16.6 - 7/10/26 - Ron Lockwood
#    The derived per-language preview specs moved to the Lib/AI subfolder (grouped with the other Work-on-Rules-with-AI runtime data); load them from there via a new AI_DATA_DIR.
#
#   Version 3.16.3 - 7/6/26 - Ron Lockwood
#    Diff highlighting is now confined to the side-by-side comparison (a new compare flag); the single-rule create/explain views render plain like XXE instead of being flagged wholesale
#    as "added" (which had tinted the whole rule green). Restyled to match XXE: Arial 16px labels/chips, the extra per-item indents from transfer.css (pattern-item .4in, attr/list-item
#    .2in), the side value coloured like the XXE combo box (red for sl, ochre for tl), and a pale-yellow (#ffffdd) comment box with grey serif-monospace text (no "//" prefix). An empty
#    value (e.g. <lit v=""/>) now renders as an empty coloured box rather than collapsing to nothing.
#
#   Version 3.16.5 - 7/7/26 - Ron Lockwood
#    Added renderRulePreviewHtml (selected rule in the left pane, right pane empty) for the immediate rule preview when a rule is clicked in the modify/explain tab.
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
import unicodedata
import xml.etree.ElementTree as ET

import Utils
import markdown

# realpath so this resolves through a per-file symlink (dev deploy) to the real Lib folder; the stylesheets live in its css subfolder (Lib/css).
CSS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'css', 'transfer_preview.css')

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
    'equal':              ('equal: ', [('caseless', 'case insensitive', 'c-checkbox')]),
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
    'begins-with':        ('begins with: ', [('caseless', 'case insensitive', 'c-checkbox')]),
    'ends-with':          ('ends with: ', [('caseless', 'case insensitive', 'c-checkbox')]),
    'begins-with-list':   ('begins with something in list: ', [('caseless', 'case insensitive', 'c-checkbox')]),
    'ends-with-list':     ('ends with something in list: ', [('caseless', 'case insensitive', 'c-checkbox')]),
    'contains-substring': ('contains substring: ', [('caseless', 'case insensitive', 'c-checkbox')]),
    'in':                 ('in list: ', [('caseless', 'case insensitive', 'c-checkbox')]),
}

# Which elements get a fold control comes from the stylesheet: the derived spec's "_collapsible" list holds exactly the elements XXE marks with a collapser() in transfer.css (see
# derive_preview_specs.py), so add/remove a collapser there and the preview follows. COLLAPSIBLE_FALLBACK is used only when the derived spec JSON is missing (the built-in SPEC has no
# "_collapsible" key); it mirrors the elements transfer.css currently collapses that can appear in a rule/def preview.
COLLAPSIBLE_FALLBACK = {'rule', 'action', 'when', 'otherwise', 'out', 'def-cat', 'def-attr', 'def-list', 'def-macro'}

# The preview shows a single whole rule, or a single whole macro, at the top. Folding that top element away would leave nothing, so rule and def-macro never get a collapser here even though
# transfer.css marks them collapsible (in XXE you see the whole file, so folding a rule there makes sense).
COLLAPSER_EXCLUDE = {'rule', 'def-macro'}

# Vertical indent guides mark the lengthy, deeply-nested logic blocks so the eye can track which rows line up with which block (like a code editor's indent guides). This is deliberately a
# DIFFERENT, preview-only set from the collapsible elements: guides go on the block-logic elements whether or not XXE lets you fold them (choose/test/and/or/not are not collapsible in
# transfer.css but still benefit from a guide), and never on the single top-level rule/macro.
INDENT_GUIDE_TAGS = {'choose', 'when', 'otherwise', 'test', 'out', 'and', 'or', 'not'}

LIB_DIR = os.path.dirname(os.path.realpath(__file__))
# The derived per-language preview specs live in the Lib/AI subfolder (grouped with the other Work-on-Rules-with-AI runtime data) rather than the Lib root.
AI_DATA_DIR = os.path.join(LIB_DIR, 'AI')
_specCache = {}

def loadSpec(lang: str) -> dict:
    '''Load the per-language display spec (labels + colours) that derive_preview_specs.py generated from transfer.css. Falls back to English, then to the built-in SPEC if no file is found,
    so the preview always renders even before the derivation has been run.'''

    lang = (lang or 'en').lower()

    if lang in _specCache:
        return _specCache[lang]

    for candidate in (lang, 'en'):

        path = os.path.join(AI_DATA_DIR, 'preview_spec_{lang}.json'.format(lang=candidate))

        if os.path.isfile(path):

            with open(path, encoding='utf-8') as specFile:
                _specCache[lang] = json.load(specFile)

            return _specCache[lang]

    _specCache[lang] = SPEC
    return SPEC

def loadCss() -> str:
    '''Read the reskin CSS so it can be inlined into the document.'''

    with open(CSS_PATH, encoding='utf-8') as cssFile:
        return cssFile.read()

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

def renderRowLine(elem: ET.Element, spec: dict, collapsible: bool = False) -> str:
    '''Render an element's header row: its label plus its displayed attributes, using the given per-language display spec. With `collapsible` a plus/minus collapser box is placed in
    front of the label (the block's children fold when it is clicked - see wrapDocument's script).'''

    collapser = '<span class="collapser"></span>' if collapsible else ''
    entry = spec.get(elem.tag)

    if entry is None:
        # Fallback: show the tag name and every attribute generically.
        pieces = ['<span class="label">' + html.escape(elem.tag) + ': </span>']
        for name, value in elem.attrib.items():
            pieces.append('<span class="attrlabel">' + html.escape(name) + ': </span>' + renderChip(value, 'c-chunk'))
        return '<span class="rowline">' + collapser + ''.join(pieces) + '</span>'

    label, attrSpecs = entry
    pieces = ['<span class="label">' + html.escape(label) + '</span>']

    for name, attrLabel, colorClass in attrSpecs:

        # The caseless check-box is always shown on the elements that support it, like XXE shows it: checked when the attribute is "yes", unchecked otherwise - including when the
        # attribute is absent, since "no" is its DTD default. Disabled because the preview reflects the rule, it isn't an editor. The label text (e.g. "case insensitive") comes from the
        # per-language spec, derived from the check-box() declaration in the XXE stylesheet.
        if colorClass == 'c-checkbox':

            pieces.append('<input type="checkbox" class="caseless-box" disabled' + (' checked' if elem.attrib.get(name) == 'yes' else '') + '>')

            if attrLabel:
                pieces.append('<span class="attrlabel">' + html.escape(attrLabel) + '</span>')

            continue

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

    return '<span class="rowline">' + collapser + ''.join(pieces) + '</span>'

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

    # Two independent, children-gated decisions (see the constants above): a collapser fold control goes on the elements transfer.css marks collapsible (minus the top-level rule/macro),
    # and a vertical indent guide - the "guide" class the CSS keys off - goes on the lengthy logic blocks. The two sets overlap (e.g. out, when) but are not the same.
    children = [c for c in elem]
    collapsible = bool(children) and elem.tag not in COLLAPSER_EXCLUDE and elem.tag in (spec.get('_collapsible') or COLLAPSIBLE_FALLBACK)
    guided = bool(children) and elem.tag in INDENT_GUIDE_TAGS

    cls = (forced or diffClass(elem, other)) if compare else ''
    classAttr = 'el ' + elem.tag + (' guide' if guided else '') + ((' ' + cls) if cls else '')

    out = ['<div class="' + classAttr + '">', renderRowLine(elem, spec, collapsible)]

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

def hasRtlText(text: str) -> bool:
    '''Return True when any character in the text has an RTL bidi class, so the explanation pane can switch direction to match the content.'''

    for char in text:

        if unicodedata.bidirectional(char) in ('R', 'AL'):
            return True

    return False


def markdownToHtml(mdText: str) -> str:
    '''Convert the explanation's Markdown to HTML with the Python-Markdown package. The whole text is HTML-escaped first: Python-Markdown passes raw HTML through untouched, and the result
    goes into a live QWebEngineView, so any markup the model emits must arrive as visible text, never as elements. The extensions cover what models commonly produce beyond the core syntax:
    tables, fenced code blocks, saner list numbering, and single-newline line breaks (nl2br, so a line break inside a paragraph shows as one, as this preview has always done).'''

    return markdown.markdown(html.escape(mdText), extensions=['tables', 'fenced_code', 'sane_lists', 'nl2br'])

# Clicking a collapser box folds/unfolds its block: toggle the "collapsed" class on the enclosing .el, which hides the children and swaps the minus icon for the plus (both in the CSS).
# One delegated listener on the document covers every collapser without per-element handlers.
COLLAPSER_SCRIPT = ('<script>document.addEventListener("click", function(e) {'
                    ' if (e.target.classList && e.target.classList.contains("collapser")) { e.target.closest(".el").classList.toggle("collapsed"); } });</script>')

def wrapDocument(bodyHtml: str, colors=None, split: bool = False) -> str:
    '''Wrap rendered body HTML in a full document with the inlined CSS (plus the derived chip-colour overrides) and the collapser click handler. With `split` the body gets the "split"
    class, which makes each .compare pane scroll on its own (see transfer_preview.css) so, e.g., the explanation stays in view while the user scrolls through a long rule on the left.'''

    return ('<!DOCTYPE html><html><head><meta charset="utf-8"><style>\n'
            + loadCss() + '\n' + colorsToCss(colors)
            + '\n</style></head><body' + (' class="split"' if split else '') + '>' + bodyHtml + COLLAPSER_SCRIPT + '</body></html>')

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

def renderRulePreviewHtml(ruleXml: str, lang: str = 'en') -> str:
    '''Render just the selected rule in the left pane, leaving the right pane empty - used when the user clicks a rule in the modify/explain list, so the rule shows immediately and there is
    room on the right for the modified version (Modify) or the explanation (Explain) to appear. `lang` selects the label language. Returns a complete HTML document.'''

    spec = loadSpec(lang)
    left = '<div class="pane">' + elementToHtml(parseFragment(ruleXml), spec=spec) + '</div>'

    return wrapDocument('<div class="compare">' + left + '</div>', spec.get('_colors'), split=True)

def renderExplanationHtml(ruleXml: str, explanationText: str, lang: str = 'en') -> str:
    '''Render the rule (styled like XXE) on the left and the AI's explanation on the right - used for the "explain" preview. The explanation arrives as Markdown and is rendered by
    markdownToHtml (which escapes everything first, so no raw markup from the model is ever shown). Returns a complete HTML document.'''

    spec = loadSpec(lang)

    left = '<div class="pane">' + elementToHtml(parseFragment(ruleXml), spec=spec) + '</div>'

    # The explanation pane switches to right-to-left layout when the explanation text contains any RTL characters in the 1st quarter of the text.
    rtlClass = ' rtl' if Utils.hasRtl(explanationText[0:len(explanationText)//4]) else ''
    right = '<div class="pane explanation' + rtlClass + '">' + markdownToHtml(explanationText) + '</div>'

    return wrapDocument('<div class="compare">' + left + right + '</div>', spec.get('_colors'), split=True)

def renderComparisonHtml(beforeXml: str, afterXml: str, lang: str = 'en') -> str:
    '''Render before/after side-by-side - used for the "modify" preview. `lang` selects the label language. Diff highlighting is best-effort (positional); the panes are always readable even
    if the highlighting is imperfect.'''

    spec = loadSpec(lang)
    before = parseFragment(beforeXml)
    after = parseFragment(afterXml)

    legend = ('<div class="legend">'
              '<span class="sw" style="background:#F7CAC9"></span>removed / changed on the left'
              '<span class="sw" style="background:#CFF5D1"></span>added on the right'
              '<span class="sw" style="background:#FFD8A8"></span>changed'
              '</div>')

    left = '<div class="pane"><h3>Before</h3>' + elementToHtml(before, after, side='before', spec=spec, compare=True) + '</div>'
    right = '<div class="pane"><h3>After</h3>' + elementToHtml(after, before, side='after', spec=spec, compare=True) + '</div>'

    return wrapDocument(legend + '<div class="compare">' + left + right + '</div>', spec.get('_colors'), split=True)
