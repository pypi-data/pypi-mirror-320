from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.constants import (
    DEFAULT_CHARACTER_WEIGHTS,
    WEAK_PASSWORD_PATTERNS,
    Character,
)


def test_analyzer_options_default_values():
    """
    Test that AnalyzerOptions initializes with the correct default values.
    """
    options = AnalyzerOptions()

    assert options.required_length == 8, "Default required_length should be 8."
    assert options.maximum_length == 64, "Default maximum_length should be 64."
    assert options.character_weights == DEFAULT_CHARACTER_WEIGHTS, "Default character_weights should match DEFAULT_CHARACTER_WEIGHTS."
    assert options.score_threshold == 0, "Default score_threshold should be 0."
    assert options.prohibited_characters == [
        " "], "Default prohibited_characters should be a list containing a space."
    assert options.weak_passwords == AnalyzerOptions.weak_passwords, "Default weak_passwords should match the pre-defined WEAK_PASSWORD_PATTERNS."


def test_analyzer_options_custom_values():
    """
    Test that AnalyzerOptions initializes correctly with custom values.
    """
    custom_character_weights = {
        Character.LOWERCASE: 2,
        Character.UPPERCASE: 3,
        Character.NUMBER: 4,
        Character.SPECIAL_CHAR: 5,
    }

    passwords = WEAK_PASSWORD_PATTERNS + ["123456", "password", "admin"]

    options = AnalyzerOptions(
        required_length=12,
        maximum_length=30,
        character_weights=custom_character_weights,
        score_threshold=10,
        prohibited_characters=["!", "@", "#"],
        weak_passwords=["123456", "password", "admin"]
    )

    assert options.required_length == 12, "Custom required_length should be 12."
    assert options.maximum_length == 30, "Custom maximum_length should be 30."
    assert options.character_weights == custom_character_weights, "Custom character_weights should match the provided dictionary."
    assert options.score_threshold == 10, "Custom score_threshold should be 10."
    assert options.prohibited_characters == [
        "!", "@", "#"], "Custom prohibited_characters should match the provided list."
    assert options.weak_passwords == passwords, "Custom weak_passwords should match the provided list."


def test_analyzer_options_partial_custom_values():
    """
    Test that AnalyzerOptions allows setting some custom values while keeping defaults for others.
    """
    passwords = WEAK_PASSWORD_PATTERNS + ["weakpass"]
    options = AnalyzerOptions(
        required_length=10,
        weak_passwords=["weakpass"]
    )

    assert options.required_length == 10, "Custom required_length should be 10."
    assert options.maximum_length == 64, "Default maximum_length should be retained as 64."
    assert options.character_weights == DEFAULT_CHARACTER_WEIGHTS, "Default character_weights should be retained."
    assert options.score_threshold == 0, "Default score_threshold should be retained as 0."
    assert options.prohibited_characters == [
        " "], "Default prohibited_characters should be retained."
    assert options.weak_passwords == passwords, "Custom weak_passwords should extend the default weak_passwords."


def test_analyzer_options_empty_initialization():
    """
    Test that AnalyzerOptions does not fail if all optional parameters are explicitly set to None or empty.
    """
    options = AnalyzerOptions(
        required_length=8,
        maximum_length=64,
        character_weights=None,
        score_threshold=0,
        prohibited_characters=[],
        weak_passwords=[]
    )

    assert options.character_weights == DEFAULT_CHARACTER_WEIGHTS, "Default character_weights should be applied if None is provided."
    assert options.prohibited_characters == [
    ], "Empty prohibited_characters should be accepted."
    assert options.weak_passwords == AnalyzerOptions.weak_passwords, "Empty weak_passwords should default to the pre-defined WEAK_PASSWORD_PATTERNS."
