"""Source and Target classes - wrappers around Phrase"""

from dataclasses import dataclass
from .phrase import Phrase
from .enums import PhraseType


@dataclass
class Source(Phrase):
    """Source phrase - a phrase on the source side of a rule"""

    def __post_init__(self):
        super().__post_init__()
        self.phrase_type = PhraseType.source


@dataclass
class Target(Phrase):
    """Target phrase - a phrase on the target side of a rule"""

    def __post_init__(self):
        super().__post_init__()
        self.phrase_type = PhraseType.target
