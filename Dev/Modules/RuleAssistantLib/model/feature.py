"""Feature model class"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from .rule_constituent import RuleConstituent
from .. import constants

if TYPE_CHECKING:
    pass


@dataclass
class Feature(RuleConstituent):
    """A linguistic feature (e.g., gender:α, number:sg)

    Attributes:
        label: Feature name (e.g., "gender", "number")
        match: Greek variable for agreement (e.g., "α", "β") - takes precedence over value
        value: Concrete value (e.g., "sg", "feminine")
        unmarked: Unmarked/default value
        ranking: Priority ranking (0 = unranked, >0 = priority order)
    """

    label: str = ""
    match: str = ""
    value: str = ""
    unmarked: str = ""
    ranking: int = 0

    def __post_init__(self):
        super().__init__()

    def get_match_or_value(self) -> str:
        """Return the effective feature value.

        Match (Greek variable) takes precedence over concrete value.

        Returns:
            The match if non-empty, otherwise the value
        """
        return self.match if self.match else self.value

    def produce_html(self, is_head: bool = False) -> str:
        """Generate HTML span for this feature.

        Args:
            is_head: Whether the parent word is marked as head

        Returns:
            Complete HTML span element for the feature
        """
        # Helper for translation at module level with fallback
        def _t(s: str) -> str:
            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistant", s)
            except ImportError:
                # Fallback for testing without Qt
                return {"FeatureX": "Feature"}.get(s, s)

        css_class = "feature headfeature" if is_head else "feature"
        html = self.produce_span(css_class, "f")

        # Label or placeholder
        label_text = self.label if self.label else _t("FeatureX")
        html += f"{label_text}:{self.get_match_or_value()}"

        # Add ranking indicator if present
        if self.ranking > 0:
            html += f'<span class="ranking feature">{self.ranking}</span>'

        # Add unmarked value if present
        if self.unmarked:
            html += f'\n<span class="unmarked feature">unmarked:{self.unmarked}</span>'

        html += "</span>"
        return html

    def duplicate(self) -> "Feature":
        """Create a deep copy of this feature.

        Returns:
            A new Feature with the same values
        """
        return Feature(
            label=self.label,
            match=self.match,
            value=self.value,
            unmarked=self.unmarked,
            ranking=self.ranking,
        )

    def assign_rankings_to_sisters(self, max_rankings: int) -> None:
        """Auto-assign rankings to sister features that don't have one.

        Fills in missing rankings using lowest available integers.
        Called when user selects a ranking for this feature.

        Args:
            max_rankings: Maximum number of ranking slots available
        """
        if not self.parent:
            return

        sisters = getattr(self.parent, "features", [])
        if not sisters:
            return

        # Build list of rankings already in use
        used_rankings = set()
        for sister in sisters:
            if hasattr(sister, "ranking") and sister.ranking > 0:
                used_rankings.add(sister.ranking)

        # Assign lowest available rankings to those without
        next_ranking = 1
        for sister in sisters:
            if hasattr(sister, "ranking") and sister.ranking == 0:
                while next_ranking in used_rankings:
                    next_ranking += 1
                sister.ranking = next_ranking
                used_rankings.add(next_ranking)

    def sister_feature_has_ranking(self) -> bool:
        """Check if any sister feature already has a ranking.

        Returns:
            True if any sibling feature has ranking > 0
        """
        if not self.parent:
            return False

        sisters = getattr(self.parent, "features", [])
        return any(hasattr(s, "ranking") and s.ranking > 0 for s in sisters if s is not self)

    def swap_ranking_of_sister_with_ranking(self, new_ranking: int, old_ranking: int) -> None:
        """Swap ranking values when user changes a feature's ranking.

        Args:
            new_ranking: The new ranking value being assigned
            old_ranking: The old ranking value being replaced
        """
        if not self.parent:
            return

        sisters = getattr(self.parent, "features", [])
        for sister in sisters:
            if sister is self:
                self.ranking = new_ranking
            elif hasattr(sister, "ranking") and sister.ranking == new_ranking:
                sister.ranking = old_ranking

    def remove_rankings_from_sisters(self) -> None:
        """Clear rankings from all sister features.

        Called when user removes ranking from this feature.
        """
        if not self.parent:
            return

        sisters = getattr(self.parent, "features", [])
        for sister in sisters:
            if hasattr(sister, "ranking"):
                sister.ranking = 0
