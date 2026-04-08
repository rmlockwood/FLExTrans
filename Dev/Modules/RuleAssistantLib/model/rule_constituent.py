"""Base class for all rule constituent elements"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .feature import Feature
    from .word import Word
    from .phrase import Phrase


class RuleConstituent:
    """Base class for all elements in a rule tree (phrases, words, features, etc.)

    Each constituent has a runtime identifier (for HTML click dispatch) and a parent
    pointer (for tree navigation).
    """

    def __init__(self):
        self.identifier: int = 0
        self.parent: Optional["RuleConstituent"] = None

    def produce_span(self, css_class: str, type_code: str) -> str:
        """Generate opening span tag for HTML with click handler.

        Args:
            css_class: CSS class(es) to apply
            type_code: Single letter type code ('p', 'w', 'c', 'f', 'a')

        Returns:
            Opening span tag with id and onmousedown handler
        """
        # CRITICAL: onmousedown not onclick so both left and right click fire
        return (
            f'<span class="{css_class}" id="{type_code}.{self.identifier}" '
            f'onmousedown="toApp(\'{type_code}.{self.identifier}\',event)">'
        )

    def produce_to_app(self, type_code: str) -> str:
        """Generate the toApp() call string for this constituent.

        Args:
            type_code: Single letter type code

        Returns:
            toApp() function call string
        """
        return f'"toApp(\'{type_code}.{self.identifier}\',event)"'

    def find_constituent(self, identifier: int) -> Optional["RuleConstituent"]:
        """Recursively find a constituent by its identifier.

        Default implementation checks if this constituent matches.
        Subclasses with children override to search recursively.

        Args:
            identifier: The identifier to search for

        Returns:
            The matching RuleConstituent or None if not found
        """
        if self.identifier == identifier:
            return self
        return None
