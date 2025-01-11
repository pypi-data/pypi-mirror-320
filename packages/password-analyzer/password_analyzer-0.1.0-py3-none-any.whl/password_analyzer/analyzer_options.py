from typing import Optional

from password_analyzer.constants import (
    DEFAULT_CHARACTER_WEIGHTS,
    WEAK_PASSWORD_PATTERNS,
    Character,
)


class AnalyzerOptions():
    required_length: int
    maximum_length: int
    character_weights: dict[Character, int]
    score_threshold: int
    prohibited_characters: list[str]
    weak_passwords: list[str] = WEAK_PASSWORD_PATTERNS

    def __init__(self, required_length: int = 8, maximum_length: int = 64, character_weights: Optional[dict[Character, int]] = None, score_threshold: int = 0, prohibited_characters: list[str] = [" "], weak_passwords: list[str] = []) -> None:
        self.required_length = required_length
        self.maximum_length = maximum_length
        self.character_weights = DEFAULT_CHARACTER_WEIGHTS if not character_weights else character_weights
        self.score_threshold = score_threshold
        self.prohibited_characters = prohibited_characters

        if len(weak_passwords) > 0:
            for p in weak_passwords:
                self.weak_passwords.append(p)
