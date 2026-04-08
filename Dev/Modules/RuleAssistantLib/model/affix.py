"""Affix model class"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from .rule_constituent import RuleConstituent
from .enums import AffixType

if TYPE_CHECKING:
    from .feature import Feature


@dataclass
class Affix(RuleConstituent):
    """An affix (prefix or suffix) attached to a word.

    Attributes:
        affix_type: AffixType.prefix or AffixType.suffix
        features: List of Feature objects on this affix
    """

    affix_type: AffixType = AffixType.suffix
    features: list["Feature"] = field(default_factory=list)

    def __post_init__(self):
        super().__init__()

    def produce_html(self, is_head: bool = False) -> str:
        """Generate HTML for this affix.

        Args:
            is_head: Whether the parent word is marked as head

        Returns:
            HTML <li> element with affix span and optional feature <ul>
        """
        affix_type_str = "prefix" if self.affix_type == AffixType.prefix else "suffix"

        html = "<li>"
        html += self.produce_span("tf-nc affix", "a")
        html += affix_type_str
        html += "</span>"

        # Add features if present
        if self.features:
            html += "<ul>\n"
            html += self._produce_features_html(is_head)
            html += "</ul>"

        html += "</li>\n"
        return html

    def _produce_features_html(self, is_head: bool = False) -> str:
        """Generate HTML for all features in this affix.

        Features are rendered as a single <li><table> with one row per feature.

        Args:
            is_head: Whether the parent word is marked as head

        Returns:
            HTML <li><table>...<tr>...<feature>...</tr></table></li>
        """
        html = "<li><table class=\"tf-nc\">\n"
        for feature in self.features:
            html += "<tr>\n<td align=\"left\">"
            html += feature.produce_html(is_head)
            html += "</td>\n</tr>\n"
        html += "</table>\n</li>\n"
        return html

    def find_constituent(self, identifier: int) -> "RuleConstituent | None":
        """Recursively search for a constituent by identifier.

        Args:
            identifier: The identifier to search for

        Returns:
            The matching RuleConstituent or None
        """
        if self.identifier == identifier:
            return self

        # Search features
        for feature in self.features:
            result = feature.find_constituent(identifier)
            if result:
                return result

        return None

    def duplicate(self) -> "Affix":
        """Create a deep copy of this affix with all its features.

        Returns:
            A new Affix with duplicate features
        """
        new_affix = Affix(affix_type=self.affix_type)
        new_affix.features = [f.duplicate() for f in self.features]
        for feature in new_affix.features:
            feature.parent = new_affix
        return new_affix

    def get_is_head(self) -> bool:
        """Check if parent word is marked as head.

        Returns:
            True if parent word has head=yes
        """
        if not self.parent:
            return False
        return getattr(self.parent, "head", None) and str(self.parent.head).lower() == "yes"
