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

if __name__ == '__main__':
    unittest.main()
