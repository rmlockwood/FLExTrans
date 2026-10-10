#
#   TransferPreview
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.17.7 - 10/10/26 - Ron Lockwood
#    Rules and macros can be folded and get indent guides (as do action and let); rule and macro names keep their colour in comparisons; folding a block no longer jumps the scroll position.
#
#   Version 3.17.6 - 10/10/26 - Ron Lockwood
#    Added renderFileComparisonHtml (two whole rules files, for the new Compare Rule Files tool) and change navigation; pane alignment now measures once, so it stays fast on a whole file.
#
#   Version 3.17.5 - 10/10/26 - Ron Lockwood
#    The comparison panes scroll together with one scrollbar and matched rows lined up; folding a block folds its twin. Elements of different kinds are no longer paired as "changed".
#
#   Version 3.17.4 - 10/10/26 - Ron Lockwood
#    On a changed row in the comparison, the parts that differ within a value or comment (e.g. the 1s of kira1.1 vs kira2.2) are highlighted in a darker orange.
#
#   Version 3.17.3 - 10/10/26 - Ron Lockwood
#    The comparison matches children on tag + attributes before tag alone, so deleting one of two literal tags marks just that one removed instead of pairing the wrong two as "changed".
#
#   Version 3.17.2 - 10/10/26 - Ron Lockwood
#    The comparison legend, Before/After headings, "New definitions" heading, and side values (source/target lang.) are now translated into the UI language.
#
#   Version 3.17.1 - 10/9/26 - Ron Lockwood
#    In the before/after comparison, chip and comment fills are white (or the row's red/green/orange diff colour on a highlighted row) and the side value is black. Added the code description block.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.12 - 7/28/26 - Ron Lockwood
#    Lexical units the model writes into an explanation (e.g. ^book1.1<n><pl><gen>$) are now color-coded like the Source/Target viewer: colorLexicalUnitsInMarkdown stashes each one past the
#    Markdown render and swaps in the colored HTML Testbed.lexicalUnitToHtml builds for it.
#
#   Version 3.16.11 - 7/24/26 - Ron Lockwood
#    Fixed literal &lt;/&gt; showing in the explanation: markdownToHtml stashed &, <, > as sentinels instead of escaping up front, so Python-Markdown no longer double-escapes them inside code spans/blocks.
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
#
#   OVERVIEW (AI generated, then edited)
#
#   Renders Apertium transfer XML (a rule, a macro, new definitions, or a whole rules file) as read-only styled HTML, so the linguist sees rules the way XXE shows them (labels, coloured
#   attribute chips, comment boxes, plus/minus collapsers) without ever seeing raw markup. It serves the AI Rule Studio's preview and the Compare Rule Files tool. The HTML is a complete
#   self-contained document (CSS inlined, scripts embedded) that the caller loads into a QWebEngineView.
#
#   THE VIEWS
#
#   renderRuleHtml - a single rule plus any new definitions (Create). renderRulePreviewHtml - the clicked rule alone in the left pane, right pane left free (Modify/Explain, before the AI answers).
#   renderExplanationHtml - the rule on the left, the AI's Markdown explanation on the right (Explain). renderComparisonHtml - before and after side by side with diff highlighting (Modify).
#   renderFileComparisonHtml - two whole rules files side by side (Compare Rule Files). Both comparisons are built by comparisonDocument, so they look and behave the same; for a file the
#   older version can go on the right (beforeOnRight), since the colours always read from the older version to the newer one.
#
#   LABELS AND COLOURS
#
#   Labels and chip colours come from a per-language spec (Lib/AI/preview_spec_<lang>.json) that derive_preview_specs.py generates from the XXE stylesheet transfer.css, so editing XXE's CSS
#   flows into the preview. The built-in SPEC is only a fallback when no JSON exists. transfer_preview.css holds the layout plus fallback colours; colorsToCss appends the derived colours after it.
#   The preview's own UI text (legend, Before/After headings, side values) isn't in the XXE stylesheet, so it goes through the Qt translator instead (context TransferPreview, translations/TransferPreview_*.ts).
#
#   DIFF HIGHLIGHTING
#
#   Only the comparison view highlights (the compare flag on elementToHtml); the single-rule views render plain. Children are aligned with difflib in two passes (alignChildren): first on the
#   full tag + attributes so identical rows pair exactly, then on the tag alone within whatever is left, so an attribute edit pairs as one "changed" row. That way an inserted or deleted node
#   marks only itself instead of shifting every later row, and deleting one of several like elements (one literal tag of two) doesn't pair the wrong two. Elements of different kinds are never
#   paired - a choose replaced by a let shows as a red block and a green one, not as an orange pair whose children get matched against unrelated rows.
#
#   Unmatched nodes are "removed" (red) on the before pane and "added" (green) on the after pane; matched nodes whose attributes or comment text differ are "changed" (orange). Only the row's own
#   header line is coloured, never its children. On a changed row, each value is also compared piece by piece (letter runs, digit runs, punctuation) with the other pane's (highlightDifferences),
#   and the differing pieces are shown darker orange: values always (a changed side value is highlighted whole), a comment only when the two are alike enough (COMMENT_DIFF_MIN_RATIO) for the
#   marks not to be noise. The comparison is wrapped in a "diffview" class that turns the normal chip and comment fills white (or the row's diff colour on a highlighted row) and the red/ochre
#   side text black, so the XXE palette doesn't compete with the diff colours. Rule names and macro names (NAME_CHIPS) are the exception and keep their colour, as landmarks in a long file.
#
#   LINED-UP SCROLLING
#
#   The two comparison panes scroll as one, with their rows level, like a side-by-side diff tool. The trap is that the panes are rendered separately, so they must agree exactly on which rows
#   pair up: alignChildrenForSide has the after pane invert the before pane's alignment rather than run its own (difflib isn't symmetric). Each matched pair gets the same data-pair id in both
#   panes ("0" for the top element, then "<parent id>.<before position>-<after position>"), and ALIGN_SCRIPT, run in the browser after layout, pads the higher twin of each pair down to its
#   partner. It re-runs on resize/zoom and on a fold; folding a block folds its twin too, and keeps the clicked row where it was on screen (COLLAPSER_SCRIPT). A pair it can't find simply
#   isn't padded - the panes stay readable either way.
#   The same script groups the highlighted rows into changes and steps through them (diffNav), for the Compare Rule Files arrow buttons; see the comment above ALIGN_SCRIPT for how it stays
#   fast on a whole file of thousands of rows.
#
#   EXPLANATION TEXT
#
#   The model's Markdown is rendered by Python-Markdown with &, <, > swapped for private-use sentinels first (see _MD_SENTINELS for why plain escaping doesn't work), so no markup from the model
#   can become live HTML. Apertium lexical units in the text (^lemma<tags>$) are stashed as placeholders and swapped back as colour-coded HTML from Testbed.lexicalUnitToHtml.
#
#   CODE STRUCTURE
#
#   loadSpec / loadCss read the display spec and the stylesheet. childKey/childSignature, alignByKind and alignChildren do the matching. highlightDifferences, renderChip and renderRowLine
#   build one element's header row; diffClass decides "changed"; elementToHtml recurses over the tree, calling alignChildrenForSide in compare mode and handing out the pair ids. parseFragment
#   parses XML keeping comments; colorsToCss turns the derived colours into CSS. markdownToHtml and colorLexicalUnitsInMarkdown render the explanation. COLLAPSER_SCRIPT and ALIGN_SCRIPT are
#   the browser-side scripts; wrapDocument wraps a body into the final document. The render*Html functions at the end are the public entry points, with comparisonDocument building both
#   comparisons and parseRuleFile reading a whole rules file for renderFileComparisonHtml.
#

import os
import re
import json
import html
import difflib
import unicodedata
import xml.etree.ElementTree as ET

from PyQt6.QtCore import QCoreApplication

import Utils
import Testbed
import markdown

# realpath so this resolves through a per-file symlink (dev deploy) to the real Lib folder; the stylesheets live in its css subfolder (Lib/css).
CSS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'css', 'transfer_preview.css')

_translate = QCoreApplication.translate

def sideLabel(value: str) -> str:
    '''Human-friendly value for the side attribute, matching the XXE combo-box labels. Translated at render time (not in a module-level dict) so the UI language's translator is already
    loaded when the string is looked up; an unexpected value is shown as is.'''

    if value == 'sl':
        return _translate('TransferPreview', 'source lang.')

    if value == 'tl':
        return _translate('TransferPreview', 'target lang.')

    return value

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

# Vertical indent guides mark the lengthy, deeply-nested blocks so the eye can track which rows line up with which block (like a code editor's indent guides) - in a whole rules file, a guide
# down the length of each rule and macro is what shows where one ends and the next begins. This is deliberately a DIFFERENT, preview-only set from the collapsible elements: guides go on these
# blocks whether or not XXE lets you fold them (choose/test/let/and/or/not are not collapsible in transfer.css but still benefit from a guide).
INDENT_GUIDE_TAGS = {'rule', 'def-macro', 'action', 'let', 'choose', 'when', 'otherwise', 'test', 'out', 'and', 'or', 'not'}

# The name chips that keep their XXE colour in the comparison, where every other chip is white (see .keep-color in transfer_preview.css): a rule's name and a macro's name in its definition.
# They are the landmarks for finding your place in a long rules file. (Element tag, attribute) pairs; a macro's name where it is called (call-macro) is not one of them.
NAME_CHIPS = {('rule', 'comment'), ('def-macro', 'n')}

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

def childSignature(elem):
    '''A stricter key than childKey: the tag plus all its attributes (or the text, for a comment), but not the element's children. Two children with the same signature are the same row, so
    the comparison pairs them first; differences further down still show, because a matched element recurses into its own children.'''

    if isComment(elem):
        return ('#comment', (elem.text or '').strip())

    return (elem.tag, tuple(sorted(elem.attrib.items())))

def alignChildren(children: list, otherChildren: list) -> list:
    '''Pair each child on this side with its counterpart on the other side, or None when it has none. Returns (child, counterpart) in this side's order.

    Two passes. First, difflib aligns on childSignature, so identical rows pair up exactly. Matching on tag alone here would go wrong when one of several like elements is deleted: with
    literal tags INF, IND before and IND after, a tag-only match pairs INF with IND (flagged "changed") and leaves the real IND looking removed. Then, within each stretch the first pass
    couldn't match, a second difflib pass on childKey (tag only) pairs like with like, so an attribute-only edit still shows as one "changed" row rather than a removed row plus an added one.
    Any surplus in a stretch has no counterpart.'''

    pairs = []
    opcodes = difflib.SequenceMatcher(None, [childSignature(c) for c in children], [childSignature(c) for c in otherChildren], autojunk=False).get_opcodes()

    for op, i1, i2, j1, j2 in opcodes:

        if op == 'equal':
            pairs.extend(zip(children[i1:i2], otherChildren[j1:j2]))

        elif op in ('replace', 'delete'):
            pairs.extend(alignByKind(children[i1:i2], otherChildren[j1:j2]))

        # 'insert' means children only on the other side; they render in that pane, not this one.

    return pairs

def alignByKind(children: list, otherChildren: list) -> list:
    '''The second pass of alignChildren: align a stretch of unmatched children by childKey (tag, or "a comment") and pair the like-for-like ones, which diffClass then flags "changed" (same
    tag, different attributes or comment text). A child with no like counterpart - including one facing a different kind of element - has none (None).'''

    pairs = []
    opcodes = difflib.SequenceMatcher(None, [childKey(c) for c in children], [childKey(c) for c in otherChildren], autojunk=False).get_opcodes()

    for op, i1, i2, j1, j2 in opcodes:

        if op == 'equal':
            pairs.extend(zip(children[i1:i2], otherChildren[j1:j2]))

        # A 'replace' here means different kinds of element (e.g. a choose where the other side has a let). One isn't an edit of the other, so they aren't paired: each is shown as
        # removed or added in its own pane rather than as a "changed" pair whose children would then be matched up against unrelated rows.
        elif op in ('replace', 'delete'):
            pairs.extend((child, None) for child in children[i1:i2])

    return pairs

# How alike two changed comments must be (difflib ratio, 0-1) before the parts that differ are picked out. A comment is prose: below this the two share little more than a few common words,
# so marking pieces would be noise and the orange row says enough. Attribute values have no threshold - they're short, and every differing piece is worth seeing.
COMMENT_DIFF_MIN_RATIO = 0.5

# The pieces highlightDifferences compares: a run of letters, a run of digits, a run of whitespace, or any other single character (punctuation such as _ . < >). Diffing whole pieces rather than
# single characters is what keeps the highlight meaningful: character by character, a_gram_cat vs a_number would pair up stray shared letters (the m, an a) and mark scattered fragments, while
# piece by piece it marks gram_cat vs number. Separating digits from letters still lets kira1.1 vs kira2.2 mark just the 1s and 2s.
_DIFF_PIECE_PATTERN = re.compile(r'[^\W\d_]+|\d+|\s+|.', re.DOTALL)

def highlightDifferences(text: str, otherText=None, minRatio: float = 0.0) -> str:
    '''Return the HTML-escaped text, with the pieces (see _DIFF_PIECE_PATTERN) that differ from otherText - the same value in the other pane - wrapped in a "diffchar" span, shown darker orange in
    the comparison. Only this side's text is marked, so pieces that exist only on the other side show up in that pane. With no otherText, an identical one, or one less alike than minRatio, the
    text is returned plain. The default minRatio of 0 always highlights (two values with nothing in common are highlighted whole).'''

    if otherText is None or text == otherText:
        return html.escape(text)

    pieces = _DIFF_PIECE_PATTERN.findall(text)
    otherPieces = _DIFF_PIECE_PATTERN.findall(otherText)
    matcher = difflib.SequenceMatcher(None, pieces, otherPieces, autojunk=False)

    if matcher.ratio() < minRatio:
        return html.escape(text)

    out = []

    for op, i1, i2, _j1, _j2 in matcher.get_opcodes():

        segment = html.escape(''.join(pieces[i1:i2]))

        # An 'insert' has nothing on this side (segment is empty), so there is nothing to mark here.
        if not segment:
            continue

        out.append(segment if op == 'equal' else '<span class="diffchar">' + segment + '</span>')

    return ''.join(out)

def renderChip(value: str, colorClass: str, otherValue=None, keepColor: bool = False) -> str:
    '''Render one attribute value. Most values are coloured chips (a bordered box); the "plain" classes (c-plain and the c-side-* side colours) are shown as plain coloured text with no box.
    `otherValue` is the same attribute's value in the other pane of a comparison, on a changed row; the parts that differ from it are highlighted (see highlightDifferences). `keepColor`
    marks a name chip (NAME_CHIPS) that keeps its colour in the comparison.'''

    shown = highlightDifferences(value, otherValue)

    if colorClass == 'c-plain' or colorClass.startswith('c-side'):
        return '<span class="{cls}">{val}</span>'.format(cls=colorClass, val=shown)

    # An empty value (e.g. <lit v=""/>, the empty string used to clear an attribute) still gets a visible coloured box: a non-breaking space gives it content, and the chip's min-width
    # keeps it from collapsing, so an empty literal reads as an (empty-valued) box rather than nothing.
    return '<span class="chip {cls}{keep}">{val}</span>'.format(cls=colorClass, keep=' keep-color' if keepColor else '', val=shown or '&nbsp;')

def renderRowLine(elem: ET.Element, spec: dict, collapsible: bool = False, changedFrom=None) -> str:
    '''Render an element's header row: its label plus its displayed attributes, using the given per-language display spec. With `collapsible` a plus/minus collapser box is placed in
    front of the label (the block's children fold when it is clicked - see wrapDocument's script). `changedFrom` is the counterpart element when this is a changed row in a comparison
    (same tag, different attributes); each attribute value then has the parts that differ from the counterpart's value highlighted.'''

    collapser = '<span class="collapser"></span>' if collapsible else ''
    entry = spec.get(elem.tag)
    otherAttrib = changedFrom.attrib if changedFrom is not None else {}

    if entry is None:

        # Fallback: show the tag name and every attribute generically.
        pieces = ['<span class="label">' + html.escape(elem.tag) + ': </span>']

        for name, value in elem.attrib.items():
            pieces.append('<span class="attrlabel">' + html.escape(name) + ': </span>' + renderChip(value, 'c-chunk', otherAttrib.get(name)))

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
        otherValue = otherAttrib.get(name)

        if name == 'side':

            # Colour the side value the way the master XXE stylesheet does: red for source language (sl), ochre for target language (tl). A changed side is a whole-value swap, so it is
            # highlighted whole rather than letter by letter: comparing against an empty string makes highlightDifferences mark every character.
            colorClass = 'c-side-sl' if value == 'sl' else 'c-side-tl'
            otherValue = '' if otherValue is not None and otherValue != value else None
            value = sideLabel(value)

        if attrLabel:
            pieces.append('<span class="attrlabel">' + html.escape(attrLabel) + '</span>')

        pieces.append(renderChip(value, colorClass, otherValue, (elem.tag, name) in NAME_CHIPS))

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

def alignChildrenForSide(children: list, otherChildren: list, side: str) -> list:
    '''alignChildren from the point of view of the pane being rendered, always worked out in the before -> after direction. The after pane inverts the before pane's answer instead of running
    its own alignment, because difflib isn't guaranteed to pair the same rows when its two inputs are swapped - and the two panes must agree on every pair for the rows to line up across them.'''

    if side == 'before':
        return alignChildren(children, otherChildren)

    counterpartOf = {id(afterChild): beforeChild for beforeChild, afterChild in alignChildren(otherChildren, children) if afterChild is not None}
    return [(child, counterpartOf.get(id(child))) for child in children]

def elementToHtml(elem, other=None, side: str = 'after', forced: str = '', spec=None, compare: bool = False, pairId: str = '') -> str:
    '''Recursively render an element to HTML.

    Diff highlighting only happens when `compare` is True (the side-by-side modify view). In the single-rule create/explain views `compare` is False and no added/changed/removed classes
    are emitted, so the rule renders plain (like XXE) rather than being flagged wholesale as "added". `other` is the positional counterpart in the compared tree; `side` is which pane we
    are rendering ("before"/"after") so a child with no counterpart is marked "removed" on the before side and "added" on the after side; `forced` propagates that marker down a subtree.
    `pairId` names a matched pair of rows: the element is rendered with it as data-pair, and its twin in the other pane carries the same id, so ALIGN_SCRIPT can line the two up.'''

    if spec is None:
        spec = SPEC

    pairAttr = ' data-pair="' + pairId + '"' if pairId else ''

    if isComment(elem):
        text = (elem.text or '').strip()
        cls = (forced or diffClass(elem, other)) if compare else ''
        classAttr = 'el comment' + ((' ' + cls) if cls else '')

        # On a changed comment, pick out the parts that differ from the counterpart comment's text.
        otherText = (other.text or '').strip() if cls == 'changed' and other is not None and isComment(other) else None

        return '<div class="' + classAttr + '"' + pairAttr + '><span class="rowline">' + highlightDifferences(text, otherText, COMMENT_DIFF_MIN_RATIO) + '</span></div>'

    # Two independent, children-gated decisions (see the constants above): a collapser fold control goes on the elements transfer.css marks collapsible (rules and macros included), and a
    # vertical indent guide - the "guide" class the CSS keys off - goes on the lengthy blocks. The two sets overlap (e.g. rule, out, when) but are not the same.
    children = [c for c in elem]
    collapsible = bool(children) and elem.tag in (spec.get('_collapsible') or COLLAPSIBLE_FALLBACK)
    guided = bool(children) and elem.tag in INDENT_GUIDE_TAGS

    cls = (forced or diffClass(elem, other)) if compare else ''
    classAttr = 'el ' + elem.tag + (' guide' if guided else '') + ((' ' + cls) if cls else '')

    # A changed row whose counterpart has the same tag differs only in its attributes, so hand the counterpart over so the parts of each value that changed can be highlighted.
    changedFrom = other if cls == 'changed' and other is not None and not isComment(other) and other.tag == elem.tag else None

    out = ['<div class="' + classAttr + '"' + pairAttr + '>', renderRowLine(elem, spec, collapsible, changedFrom)]

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

            # Line this element's children up with the counterpart's (see alignChildren). A matched child recurses, so an attribute change is caught by diffClass; a child with no counterpart
            # is "added" on the after pane and "removed" on the before pane.
            otherChildren = [c for c in other] if other is not None else []
            unmatched = 'added' if side == 'after' else 'removed'

            # Positions of each child among its siblings, for the pair ids. An id is always "<before position>-<after position>" under the parent's id, whichever pane is rendering, so
            # the two twins of a pair get the same id.
            positionOf = {id(c): i for i, c in enumerate(children)}
            otherPositionOf = {id(c): i for i, c in enumerate(otherChildren)}

            for child, counterpart in alignChildrenForSide(children, otherChildren, side):

                if counterpart is None:
                    out.append(elementToHtml(child, forced=unmatched, side=side, spec=spec, compare=compare))

                else:
                    mine, theirs = positionOf[id(child)], otherPositionOf[id(counterpart)]
                    childPairId = '{p}.{b}-{a}'.format(p=pairId, b=mine if side == 'before' else theirs, a=theirs if side == 'before' else mine)
                    out.append(elementToHtml(child, counterpart, side, '', spec, compare, childPairId))

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


# Private-use sentinels standing in for &, <, > while Python-Markdown runs. We must keep the model's raw markup out of the live QWebEngineView, but escaping to &amp;/&lt;/&gt; up front backfires:
# inside code spans and fenced blocks Python-Markdown escapes the & of those entities a second time (&amp;lt; ...), which then shows on screen as the literal text "&lt;"/"&gt;". Swapping the three
# characters for sentinels Markdown never touches sidesteps that - Markdown can neither build raw HTML from them nor re-escape them - and we turn the sentinels back into real entities afterwards.
_MD_SENTINELS = (('&', ''), ('<', ''), ('>', ''))

def markdownToHtml(mdText: str) -> str:
    '''Convert the explanation's Markdown to HTML with the Python-Markdown package. Any raw markup the model emits must arrive as visible text, never as live elements (the result goes into a live
    QWebEngineView), so &, <, and > are stashed as private-use sentinels before rendering and restored as HTML entities after - see _MD_SENTINELS for why we can't simply html.escape up front. The
    extensions cover what models commonly produce beyond the core syntax: tables, fenced code blocks, saner list numbering, and single-newline line breaks (nl2br, so a line break inside a paragraph shows as one).'''

    # Stash &, <, > as sentinels so Markdown treats them as plain text (no raw HTML, no entity re-escaping inside code).
    for char, sentinel in _MD_SENTINELS:
        mdText = mdText.replace(char, sentinel)

    rendered = markdown.markdown(mdText, extensions=['tables', 'fenced_code', 'sane_lists', 'nl2br'])

    # Restore each sentinel to the HTML entity it stood for, so the character shows as itself in the rendered output.
    for char, sentinel in _MD_SENTINELS:
        rendered = rendered.replace(sentinel, html.escape(char))

    return rendered

# An Apertium lexical unit as the model tends to write it into an explanation: a ^...$ token whose body carries at least one <tag>, e.g. ^book1.1<n><pl><gen>$. Requiring a tag keeps ordinary prose
# that merely happens to sit between a ^ and a $ (or a lone currency $) from being mistaken for a lexical unit; the body may not itself contain a ^ or $, so each token stops at the first closing $.
_LEXICAL_UNIT_PATTERN = re.compile(r'\^([^\^$]*<[^\^$]+>[^\^$]*)\$')

# Private-use placeholders (a different PUA block from markdownToHtml's _MD_SENTINELS so the two schemes can't collide) that hold a lexical unit's spot while the surrounding Markdown renders. The
# index between them makes each placeholder unique; Markdown neither reformats nor escapes these characters, so the colored HTML we swap back in afterward lands exactly where the token was.
_LU_PLACEHOLDER_OPEN = ''
_LU_PLACEHOLDER_CLOSE = ''

def colorLexicalUnitsInMarkdown(mdText: str) -> str:
    '''Render the explanation's Markdown, but color any Apertium lexical units the model wrote into it (^book1.1<n><pl><gen>$ and the like) the same way the Source/Target viewer does, rather than
    leaving them as raw ^...<...>...$ text. Each lexical unit is pulled out and replaced by a private-use placeholder before the Markdown is rendered - so Markdown can neither reformat nor escape its
    angle brackets - then, once the Markdown is HTML, each placeholder is swapped for the colored HTML that Testbed.lexicalUnitToHtml builds for that unit (which reuses the viewer's coloring code).'''

    coloredByPlaceholder = {}

    def stashLexicalUnit(match):

        placeholder = _LU_PLACEHOLDER_OPEN + str(len(coloredByPlaceholder)) + _LU_PLACEHOLDER_CLOSE
        coloredByPlaceholder[placeholder] = Testbed.lexicalUnitToHtml(match.group(1))

        return placeholder

    stashed = _LEXICAL_UNIT_PATTERN.sub(stashLexicalUnit, mdText)
    rendered = markdownToHtml(stashed)

    # Put each colored lexical unit back where its placeholder sits in the now-rendered HTML.
    for placeholder, coloredHtml in coloredByPlaceholder.items():
        rendered = rendered.replace(placeholder, coloredHtml)

    return rendered

# Clicking a collapser box folds/unfolds its block: toggle the "collapsed" class on the enclosing .el, which hides the children and swaps the minus icon for the plus (both in the CSS).
# One delegated listener on the document covers every collapser without per-element handlers. In the comparison a block's twin in the other pane (same data-pair) is folded to match, and
# the panes are re-aligned (alignPanes, from ALIGN_SCRIPT, exists only in the comparison document).
#
# The clicked row must stay put on screen. Folding changes the height of everything below it, and in the comparison the re-alignment first strips all the padding, which can shrink the page
# under the current scroll position and make the browser pull it back - so far down a long file the view jumped somewhere else. The row's screen position is noted before the fold and the
# scrolling area (the joined comparison panes, a split view's own pane, or the page) is moved afterwards by however far the row drifted.
COLLAPSER_SCRIPT = '''<script>
document.addEventListener("click", function(e) {
    if (!(e.target.classList && e.target.classList.contains("collapser"))) { return; }
    var block = e.target.closest(".el");
    var row = block.firstElementChild;
    var scroller = block.closest(".compare.diffview") || (document.body.classList.contains("split") && block.closest(".pane")) || document.scrollingElement;
    var topBefore = row.getBoundingClientRect().top;

    block.classList.toggle("collapsed");
    var pair = block.getAttribute("data-pair");
    if (pair) { document.querySelectorAll('.el[data-pair="' + pair + '"]').forEach(function(twin) { twin.classList.toggle("collapsed", block.classList.contains("collapsed")); }); }
    if (window.alignPanes) { window.alignPanes(); }

    scroller.scrollTop += row.getBoundingClientRect().top - topBefore;
});
</script>'''

# The browser-side half of the comparison: lining the panes up, and finding and stepping through the changes. Kept as one readable block of JavaScript rather than concatenated one-liners.
#
# alignPanes lines up the Before and After panes, which scroll together as one (see .diffview in transfer_preview.css). Every matched pair of rows carries the same data-pair id in both panes;
# whichever twin sits higher gets top padding that brings its row level with the other, so a removed or added block leaves a matching gap in the opposite pane, like a side-by-side diff tool.
# Two things keep it fast and exact on a whole rule file of thousands of rows. Every position is read before anything is changed, so the browser lays the page out once instead of once per
# row; and because padding a row pushes it and everything after it in its pane down by exactly that amount, a running total per pane gives each later row's position without re-measuring.
# That relies on the pairs being in the same order in both panes, which alignChildren guarantees. Padding is used rather than margin because a margin can merge with the margin of a comment box
# inside the row instead of adding to it, which would throw the running total off. A twin hidden inside a folded block (offsetParent is null) is skipped. Both panes then get the same minimum
# height so their borders end together.
#
# findHunks groups the highlighted rows into the changes the next/previous buttons step through. A row inside an added or removed block belongs to that block's change; a changed row counts
# only its own line, an added or removed one its whole block; and rows that touch or overlap (a run of consecutive changes, or a removed block facing the added block that replaced it) are one
# change. diffNav(direction) scrolls to the next (1) or previous (-1) change, outlines it, and returns [its number, how many there are] - [0, n] when there is none that way. Pressed again
# without the user scrolling in between, it steps from the change it last showed; after a manual scroll it steps from where the user scrolled to. diffSummary re-aligns and returns the count.
#
# Everything re-runs whenever the layout can change: on load, on resize (which also covers the dialog's zoom) and on a fold (COLLAPSER_SCRIPT calls alignPanes). alignPanes puts the scroll
# position back afterwards, because stripping the old padding can briefly shrink the page and make the browser pull the scroll position up.
ALIGN_SCRIPT = '''<script>
var diffHunks = [];
var currentHunk = -1;
var lastScrollSet = null;
var NAV_MARGIN = 40;

function alignPanes() {
    var panes = document.querySelectorAll(".diffview > .pane");
    if (panes.length < 2) { return; }
    var left = panes[0], right = panes[1];
    var container = document.querySelector(".compare.diffview");
    var scrollTop = container.scrollTop;

    document.querySelectorAll(".diffview .el[data-pair]").forEach(function(row) { row.style.paddingTop = ""; });
    left.style.minHeight = "";
    right.style.minHeight = "";

    var twinOf = {};
    right.querySelectorAll(".el[data-pair]").forEach(function(row) { twinOf[row.getAttribute("data-pair")] = row; });

    var pairs = [];
    left.querySelectorAll(".el[data-pair]").forEach(function(leftRow) {
        var rightRow = twinOf[leftRow.getAttribute("data-pair")];
        if (!rightRow || !leftRow.offsetParent || !rightRow.offsetParent) { return; }
        pairs.push([leftRow, rightRow, leftRow.firstElementChild.getBoundingClientRect().top, rightRow.firstElementChild.getBoundingClientRect().top]);
    });

    var leftShift = 0, rightShift = 0, padding = [];
    pairs.forEach(function(pair) {
        var gap = (pair[2] + leftShift) - (pair[3] + rightShift);
        if (gap > 0.5) { padding.push([pair[1], gap]); rightShift += gap; }
        else if (gap < -0.5) { padding.push([pair[0], -gap]); leftShift -= gap; }
    });
    padding.forEach(function(item) { item[0].style.paddingTop = item[1] + "px"; });

    var height = Math.max(left.offsetHeight, right.offsetHeight);
    left.style.minHeight = height + "px";
    right.style.minHeight = height + "px";
    container.scrollTop = scrollTop;
    findHunks();
}

function findHunks() {
    var container = document.querySelector(".compare.diffview");
    diffHunks = [];
    if (!container) { return; }
    var base = container.getBoundingClientRect().top - container.scrollTop;

    var spans = [];
    container.querySelectorAll(".el.changed, .el.added, .el.removed").forEach(function(row) {
        if (row.parentElement.closest(".el.added, .el.removed") || !row.offsetParent) { return; }
        var top = row.firstElementChild.getBoundingClientRect().top;
        var bottom = (row.classList.contains("changed") ? row.firstElementChild : row).getBoundingClientRect().bottom;
        spans.push({top: top - base, bottom: bottom - base, rows: [row]});
    });
    spans.sort(function(a, b) { return a.top - b.top; });

    spans.forEach(function(span) {
        var last = diffHunks[diffHunks.length - 1];
        if (last && span.top <= last.bottom + 2) { last.bottom = Math.max(last.bottom, span.bottom); last.rows = last.rows.concat(span.rows); }
        else { diffHunks.push(span); }
    });
}

function diffNav(direction) {
    var container = document.querySelector(".compare.diffview");
    if (!container || !diffHunks.length) { return [0, 0]; }
    var target = -1;

    if (currentHunk >= 0 && container.scrollTop === lastScrollSet) {
        target = currentHunk + direction;
    } else {
        var reference = container.scrollTop + NAV_MARGIN;
        for (var i = 0; i < diffHunks.length; i++) {
            if (direction > 0 && diffHunks[i].top > reference + 2) { target = i; break; }
            if (direction < 0 && diffHunks[i].top < reference - 2) { target = i; }
        }
    }

    if (target < 0 || target >= diffHunks.length) { return [currentHunk >= 0 && container.scrollTop === lastScrollSet ? currentHunk + 1 : 0, diffHunks.length]; }

    document.querySelectorAll(".current-change").forEach(function(row) { row.classList.remove("current-change"); });
    diffHunks[target].rows.forEach(function(row) { row.classList.add("current-change"); });
    container.scrollTop = Math.max(0, diffHunks[target].top - NAV_MARGIN);
    lastScrollSet = container.scrollTop;
    currentHunk = target;
    return [target + 1, diffHunks.length];
}

function diffSummary() {
    alignPanes();
    return diffHunks.length;
}

window.alignPanes = alignPanes;
window.addEventListener("load", alignPanes);
window.addEventListener("resize", alignPanes);
</script>'''

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

        body.append('<div class="legend">' + html.escape(_translate('TransferPreview', 'New definitions to be added:')) + '</div>')

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
    right = '<div class="pane explanation' + rtlClass + '">' + colorLexicalUnitsInMarkdown(explanationText) + '</div>'

    return wrapDocument('<div class="compare">' + left + right + '</div>', spec.get('_colors'), split=True)

def comparisonDocument(before: ET.Element, after: ET.Element, spec: dict, leftHeading: str = '', rightHeading: str = '', beforeOnRight: bool = False) -> str:
    '''Build the side-by-side comparison document for two parsed trees - shared by the AI Rule Studio's modify preview (two versions of one rule) and the Compare Rule Files tool (two versions
    of a whole rules file). The headings are optional because the Compare Rule Files window names each side in a combo box above its pane instead.

    The colours always describe the change from `before` to `after` (removed = only in before, added = only in after). Normally before is the left pane; with beforeOnRight the panes swap, for
    a caller whose older version is on the right. Only the pane order changes - the pair ids don't depend on it, so the panes still line up.'''

    # The legend and pane headings are UI text, so they go through the Qt translator like the dialog's own strings (escaped, since a translation lands in the HTML).
    legend = ('<div class="legend">'
              '<span class="sw" style="background:#F7CAC9"></span>' + html.escape(_translate('TransferPreview', 'removed')) +
              '<span class="sw" style="background:#CFF5D1"></span>' + html.escape(_translate('TransferPreview', 'added')) +
              '<span class="sw" style="background:#FFD8A8"></span>' + html.escape(_translate('TransferPreview', 'changed')) +
              '</div>')

    leftTitle = '<h3>' + html.escape(leftHeading) + '</h3>' if leftHeading else ''
    rightTitle = '<h3>' + html.escape(rightHeading) + '</h3>' if rightHeading else ''

    # The two top-level elements are the first matched pair ("0"); every matched descendant's pair id builds on it, so ALIGN_SCRIPT can line the panes up row for row.
    beforeHtml = elementToHtml(before, after, side='before', spec=spec, compare=True, pairId='0')
    afterHtml = elementToHtml(after, before, side='after', spec=spec, compare=True, pairId='0')

    left = '<div class="pane">' + leftTitle + (afterHtml if beforeOnRight else beforeHtml) + '</div>'
    right = '<div class="pane">' + rightTitle + (beforeHtml if beforeOnRight else afterHtml) + '</div>'

    # The diffview class turns the normal chip and comment-box fills white (or the row's diff colour on a highlighted row) and the side text black, so only the diff colours stand out, and
    # makes the two panes scroll as one - see transfer_preview.css.
    return wrapDocument(legend + '<div class="compare diffview">' + left + right + '</div>' + ALIGN_SCRIPT, spec.get('_colors'), split=True)

def renderComparisonHtml(beforeXml: str, afterXml: str, lang: str = 'en') -> str:
    '''Render before/after side-by-side - used for the "modify" preview. `lang` selects the label language. Diff highlighting is best-effort (positional); the panes are always readable even
    if the highlighting is imperfect.'''

    return comparisonDocument(parseFragment(beforeXml), parseFragment(afterXml), loadSpec(lang), _translate('TransferPreview', 'Before'), _translate('TransferPreview', 'After'))

def parseRuleFile(path: str) -> ET.Element:
    '''Parse a whole transfer rules file, keeping its comments, and return the root (<transfer>, or <interchunk>/<postchunk> for the later phases). The DOCTYPE line's external DTD is not
    fetched. Raises OSError or ET.ParseError for the caller to report.'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.parse(path, parser=parser).getroot()

def renderFileComparisonHtml(beforePath: str, afterPath: str, lang: str = 'en', beforeOnRight: bool = False) -> str:
    '''Render two whole transfer rules files side by side - used by the Compare Rule Files tool. The colours describe the change from beforePath (the older version) to afterPath; beforeOnRight
    puts the older one in the right pane. Rules, macros and definitions are matched up by name wherever they sit in the file (see alignChildren), so a moved or renamed one doesn't throw the
    rest out of step. Raises OSError or ET.ParseError when a file can't be read or isn't well-formed XML.'''

    return comparisonDocument(parseRuleFile(beforePath), parseRuleFile(afterPath), loadSpec(lang), beforeOnRight=beforeOnRight)
