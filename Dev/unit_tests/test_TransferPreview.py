#
#   test_TransferPreview
#
#   Unit tests for the pure-Python parts of Dev/Lib/TransferPreview.py - mainly the Markdown
#   rendering the explanation preview uses (Python-Markdown behind an escape-first wrapper; the
#   module has no Qt dependency - the HTML it produces is only ever rendered inside a
#   QWebEngineView by the dialog).
#
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

import TransferPreview

class TestMarkdownToHtml(unittest.TestCase):

    def test_paragraphs(self):

        out = TransferPreview.markdownToHtml('first paragraph\n\nsecond paragraph')

        self.assertIn('<p>first paragraph</p>', out)
        self.assertIn('<p>second paragraph</p>', out)

    def test_single_newline_becomes_break(self):

        # The nl2br extension turns a line break inside a paragraph into a visible break.
        out = TransferPreview.markdownToHtml('line one\nline two')

        self.assertIn('<br', out)

    def test_heading(self):

        out = TransferPreview.markdownToHtml('## What the pattern matches\n\nsome text')

        self.assertIn('<h2>What the pattern matches</h2>', out)
        self.assertIn('<p>some text</p>', out)

    def test_bold_italic_code(self):

        out = TransferPreview.markdownToHtml('a **bold** and *slanted* and `coded` word')

        self.assertIn('<strong>bold</strong>', out)
        self.assertIn('<em>slanted</em>', out)
        self.assertIn('<code>coded</code>', out)

    def test_bullet_list(self):

        out = TransferPreview.markdownToHtml('- first\n- second\n\nafter')

        self.assertIn('<ul>', out)
        self.assertIn('<li>first</li>', out)
        self.assertIn('<li>second</li>', out)
        self.assertIn('<p>after</p>', out)

    def test_numbered_list(self):

        out = TransferPreview.markdownToHtml('1. one\n2. two')

        self.assertIn('<ol>', out)
        self.assertIn('<li>one</li>', out)
        self.assertIn('<li>two</li>', out)

    def test_table(self):

        out = TransferPreview.markdownToHtml('| tag | meaning |\n| --- | --- |\n| pl | plural |')

        self.assertIn('<table>', out)
        self.assertIn('<th>tag</th>', out)
        self.assertIn('<td>pl</td>', out)

    def test_fenced_code_block(self):

        out = TransferPreview.markdownToHtml('```\nsome literal lines\n```')

        self.assertIn('<pre><code>some literal lines', out)

    def test_html_is_escaped(self):

        # Raw markup from the model must never pass through as live elements - Python-Markdown would pass raw HTML untouched, so the wrapper escapes everything first.
        out = TransferPreview.markdownToHtml('a <script>bad()</script> tag and <3s_POSS>')

        self.assertNotIn('<script>', out)
        self.assertIn('&lt;script&gt;', out)
        self.assertIn('&lt;3s_POSS&gt;', out)

class TestWrapDocument(unittest.TestCase):

    def test_split_class_only_when_asked(self):

        plain = TransferPreview.wrapDocument('BODY')
        split = TransferPreview.wrapDocument('BODY', split=True)

        self.assertIn('<body>', plain)
        self.assertIn('<body class="split">', split)

    def test_collapser_script_included(self):

        out = TransferPreview.wrapDocument('BODY')

        self.assertIn('classList.toggle("collapsed")', out)

    def test_render_explanation_html_sets_rtl_class_for_rtl_text(self):

        out = TransferPreview.renderExplanationHtml('<rule comment="R"><pattern><pattern-item n="c_n"/></pattern></rule>', 'مرحبا بالعالم')

        self.assertIn('pane explanation rtl', out)

# A rule exercising the block elements and the caseless checkbox. transfer.css marks rule/action/when/out collapsible (but the top-level rule is excluded in the preview); the separate
# indent-guide set is choose/when/otherwise/test/out/and/or/not.
RULE_WITH_BLOCKS = ('<rule comment="R"><pattern><pattern-item n="c_n"/></pattern><action><choose><when><test>'
                    '<equal caseless="yes"><clip pos="1" side="sl" part="lem"/><lit v="x"/></equal></test>'
                    '<out><lu><clip pos="1" side="tl" part="whole"/></lu></out></when></choose></action></rule>')

class TestBlockRendering(unittest.TestCase):

    def test_collapsers_from_stylesheet_minus_top_level(self):

        out = TransferPreview.renderRuleHtml(RULE_WITH_BLOCKS)

        # action, when, and out carry a collapser() in transfer.css and have children; the top-level rule is excluded, and choose/test are not collapsible in transfer.css.
        self.assertEqual(out.count('<span class="collapser">'), 3)

    def test_top_level_rule_and_macro_get_no_collapser(self):

        # The whole rule (or macro) is the only thing shown, so it is never foldable - even though transfer.css marks both collapsible for the full-file XXE view.
        ruleOut = TransferPreview.renderRuleHtml('<rule comment="R"><pattern><pattern-item n="c_n"/></pattern></rule>')
        macroOut = TransferPreview.renderRuleHtml('<def-macro n="m_x" npar="1"><let><var n="v"/><lit v=""/></let></def-macro>')

        # Neither the rule nor the macro (nor their non-collapsible children here) produces a collapser.
        self.assertNotIn('<span class="collapser">', ruleOut)
        self.assertNotIn('<span class="collapser">', macroOut)

    def test_indent_guides_are_a_separate_set(self):

        out = TransferPreview.renderRuleHtml(RULE_WITH_BLOCKS)

        # Guides go on the lengthy logic blocks, including choose and test, which are NOT collapsible.
        for tag in ('choose', 'when', 'test', 'out'):
            self.assertIn('el ' + tag + ' guide', out)

        # action has a collapser but is not in the guide set; the top-level rule gets neither.
        self.assertNotIn('el action guide', out)
        self.assertNotIn('el rule guide', out)

    def test_guides_on_and_or_not(self):

        out = TransferPreview.renderRuleHtml('<rule comment="R"><action><choose><when><test>'
                                             '<and><not><equal><lit v="a"/><lit v="b"/></equal></not><or><equal><lit v="c"/><lit v="d"/></equal></or></and>'
                                             '</test><out><lu><clip pos="1" side="tl" part="whole"/></lu></out></when></choose></action></rule>')

        for tag in ('and', 'or', 'not'):
            self.assertIn('el ' + tag + ' guide', out)

    def test_empty_block_gets_neither(self):

        # otherwise is both collapsible and in the guide set, but empty here: nothing to fold or to guide. Only action (with children) yields a collapser; choose is not collapsible.
        out = TransferPreview.renderRuleHtml('<rule comment="R"><action><choose><otherwise/></choose></action></rule>')

        self.assertNotIn('otherwise guide', out)
        self.assertEqual(out.count('<span class="collapser">'), 1)   # action only

    def test_caseless_checkbox_checked(self):

        out = TransferPreview.renderRuleHtml(RULE_WITH_BLOCKS)

        self.assertIn('<input type="checkbox" class="caseless-box" disabled checked>', out)
        self.assertIn('case insensitive', out)

    def test_caseless_checkbox_unchecked_when_absent(self):

        # The checkbox always shows on elements that support caseless; an absent attribute means "no" (the DTD default), so it renders unchecked.
        out = TransferPreview.renderRuleHtml('<rule comment="R"><action><choose><when><test><equal><lit v="a"/><lit v="b"/></equal></test></when></choose></action></rule>')

        self.assertIn('<input type="checkbox" class="caseless-box" disabled>', out)
        self.assertNotIn('disabled checked', out)

if __name__ == '__main__':
    unittest.main()
