from enum import Enum


class Character(Enum):
    LOWERCASE = 1
    UPPERCASE = 2
    NUMBER = 3
    SPECIAL_CHAR = 4


DEFAULT_CHARACTER_WEIGHTS: dict[Character, int] = {
    Character.LOWERCASE: 1,
    Character.UPPERCASE: 2,
    Character.NUMBER: 3,
    Character.SPECIAL_CHAR: 4,
}


WEAK_PASSWORD_PATTERNS = [
    "password",
    "admin",
    "qwerty",
    "asdfgh",
    "zxcvbn",
    "1234",
    "123",
    "root",
    "letmein",
    "aaaaaa",
    "abcdef"
]
