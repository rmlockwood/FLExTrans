"""Category model class (runtime-only)"""

from dataclasses import dataclass
from typing import Optional
from .rule_constituent import RuleConstituent


@dataclass
class Category(RuleConstituent):
    """A grammatical category (runtime-only, not serialized).

    Category is a runtime wrapper around a word's category string.
    It's created after XML load from the word's category attribute.

    Attributes:
        name: Category abbreviation (e.g., "n", "v", "def")
    """

    name: str = ""

    def __post_init__(self):
        super().__init__()

    def produce_html(self) -> str:
        """Generate HTML span for source word category.

        Returns:
            HTML span with class 'category' and id 'c.{identifier}'
        """
        return f'{self.produce_span("category", "c")}cat:{self.name}</span>'

    def produce_html_target(self, word_identifier: int) -> str:
        """Generate HTML span for target word category.

        CRITICAL: Uses word's identifier (not own) and onclick (not onmousedown)
        so clicking a target category fires the WORD context menu.

        Args:
            word_identifier: The parent word's identifier

        Returns:
            HTML span with class 'categorytgt' and id 'w.{word_identifier}'
        """
        # Note: onclick not onmousedown, and uses word's identifier not own
        return (
            f'<span class="categorytgt" id="w.{word_identifier}" '
            f'onclick="toApp(\'w.{word_identifier}\',event)">cat:{self.name}</span>'
        )
