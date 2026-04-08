"""Web Page Producer - generates HTML for the grammar tree display"""

from pathlib import Path
from typing import TYPE_CHECKING

from .rule_id_parent_setter import RuleIdentifierAndParentSetter

if TYPE_CHECKING:
    from ..model.flex_trans_rule import FLExTransRule


class WebPageProducer:
    """Generates HTML pages for displaying rules in the QWebEngineView.

    The produced HTML uses Treeflex CSS to render linguistic phrase-structure trees
    and includes JavaScript for click-to-edit interactions via QWebChannel.
    """

    def __init__(self, css_assets_dir: str = None):
        """Initialize the producer and load CSS assets.

        Args:
            css_assets_dir: Directory containing CSS files (default: src-py/assets)
        """
        self._treeflex_css = ""
        self._rulegen_css = ""
        self._load_css_files(css_assets_dir)

    def _load_css_files(self, css_assets_dir: str = None) -> None:
        """Load CSS files into memory for embedding in HTML.

        Args:
            css_assets_dir: Directory containing CSS files
        """
        if css_assets_dir is None:
            # Assume CSS files are in src-py/assets
            base_dir = Path(__file__).parent.parent / "assets"
        else:
            base_dir = Path(css_assets_dir)

        treeflex_file = base_dir / "treeflex.css"
        rulegen_file = base_dir / "rulegen.css"

        try:
            if treeflex_file.exists():
                self._treeflex_css = treeflex_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not load treeflex.css: {e}")

        try:
            if rulegen_file.exists():
                self._rulegen_css = rulegen_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not load rulegen.css: {e}")

    def produce_web_page(self, rule: "FLExTransRule") -> str:
        """Generate complete HTML page for a rule.

        Args:
            rule: The FLExTransRule to display

        Returns:
            Complete HTML document as string
        """
        # First, assign identifiers and parent pointers to all nodes
        RuleIdentifierAndParentSetter().set_identifiers_and_parents(rule)

        # Generate HTML
        html = self._html_head(rule.name)
        html += self._html_body(rule)
        html += "</body>\n</html>"

        return html

    def _html_head(self, title: str) -> str:
        """Generate HTML head section with CSS and JavaScript.

        Args:
            title: Page title

        Returns:
            HTML head element
        """
        return (
            '<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            "<head>"
            f"<title>{title}</title>\n"
            '<meta charset="utf-8"/>\n'
            "<style>\n"
            f"{self._treeflex_css}\n"
            f"{self._rulegen_css}\n"
            "</style>\n"
            f"{self._javascript()}\n"
            "</head>\n"
            "<body>\n"
        )

    def _html_body(self, rule: "FLExTransRule") -> str:
        """Generate HTML body with source and target phrase trees.

        Args:
            rule: The rule to display

        Returns:
            HTML body content (table with source | arrow | target)
        """
        return (
            "<table>\n<tr>\n"
            + self._phrase_td(rule.source)
            + '<td>\n<span class="arrow"/>\n</td>\n'
            + self._phrase_td(rule.target)
            + "</tr>\n</table>\n"
        )

    def _phrase_td(self, phrase) -> str:
        """Generate table cell containing a phrase tree.

        Args:
            phrase: The Phrase to display

        Returns:
            HTML <td> with Treeflex wrapper and phrase HTML
        """
        return (
            '<td valign="top">\n'
            '<span class="tf-tree tf-gap-sm">\n'
            "<ul>\n"
            + phrase.produce_html()
            + "\n</ul>\n"
            "</span>\n"
            "</td>\n"
        )

    def _javascript(self) -> str:
        """Generate JavaScript section with QWebChannel bridge.

        CRITICAL: Uses QWebChannel (not direct object injection).
        The qrc:///qtwebchannel/qwebchannel.js URL is provided by Qt automatically
        when a QWebChannel is attached to the page.

        Returns:
            JavaScript section with toApp() function and QWebChannel init
        """
        return (
            '<script src="qrc:///qtwebchannel/qwebchannel.js"></script>\n'
            "<script>\n"
            "document.addEventListener('DOMContentLoaded', function() {\n"
            "    new QWebChannel(qt.webChannelTransport, function(channel) {\n"
            "        window.ftRuleGenApp = channel.objects.ftRuleGenApp;\n"
            "    });\n"
            "});\n"
            "\n"
            "function toApp(msg, event) {\n"
            "    if (window.ftRuleGenApp) {\n"
            "        ftRuleGenApp.setXCoord(event.screenX);\n"
            "        ftRuleGenApp.setYCoord(event.screenY);\n"
            "        ftRuleGenApp.setItemClickedOn(msg);\n"
            "    }\n"
            "    return false;\n"
            "}\n"
            "</script>\n"
        )
