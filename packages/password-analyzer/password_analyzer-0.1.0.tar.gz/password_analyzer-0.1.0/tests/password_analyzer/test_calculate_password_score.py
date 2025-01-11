import pytest

from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.constants import Character
from password_analyzer.password_analyzer import PasswordAnalyzer


@pytest.fixture
def password_analyzer():
    """
    Fixture to provide a PasswordAnalyzer instance with a default password.
    """
    return PasswordAnalyzer("ValidPassword123!")


@pytest.fixture
def custom_character_weights():
    """
    Provides custom character weights for testing.
    """
    return {
        Character.LOWERCASE: 2,
        Character.UPPERCASE: 3,
        Character.NUMBER: 4,
        Character.SPECIAL_CHAR: 5,
    }


def test_calculate_password_score_default_weights(password_analyzer: PasswordAnalyzer):
    """
    Test that the method correctly calculates the password score with default weights.
    """
    expected_score = (
        11 * 1  # 11 lowercase letters
        + 2 * 2  # 2 uppercase letters
        + 3 * 3  # 3 digits
        + 1 * 4  # 1 special character
    )
    method = getattr(password_analyzer,
                     "_PasswordAnalyzer__calculate_password_score")
    score = method()
    assert score == expected_score, f"Expected score {
        expected_score}, but got {score}"


def test_calculate_password_score_custom_weights(password_analyzer: PasswordAnalyzer, custom_character_weights: dict[Character, int]):
    """
    Test that the method correctly calculates the password score with custom character weights.
    """
    password_analyzer._PasswordAnalyzer__validators.get_analyzer_options = lambda: AnalyzerOptions(  # type:ignore
        character_weights=custom_character_weights
    )

    # Using custom weights
    expected_score = (
        11 * custom_character_weights[Character.LOWERCASE]
        + 2 * custom_character_weights[Character.UPPERCASE]
        + 3 * custom_character_weights[Character.NUMBER]
        + 1 * custom_character_weights[Character.SPECIAL_CHAR]
    )

    method = getattr(password_analyzer,
                     "_PasswordAnalyzer__calculate_password_score")
    score = method()
    assert score == expected_score, f"Expected score {
        expected_score}, but got {score}"


def test_calculate_password_score_empty_password():
    """
    Test that an empty password results in a score of 0.
    """
    password_analyzer = PasswordAnalyzer("")
    method = getattr(password_analyzer,
                     "_PasswordAnalyzer__calculate_password_score")
    score = method()
    assert score == 0, f"Expected score 0, but got {score}"


def test_calculate_password_score_special_characters_only():
    """
    Test that a password with only special characters calculates the correct score.
    """
    password_analyzer = PasswordAnalyzer("!@#$%^&*")
    expected_score = 8 * 4  # 8 special characters, default weight is 4
    method = getattr(password_analyzer,
                     "_PasswordAnalyzer__calculate_password_score")
    score = method()
    assert score == expected_score, f"Expected score {
        expected_score}, but got {score}"


def test_calculate_password_score_custom_weights_special_characters_only(custom_character_weights: dict[Character, int]):
    """
    Test that a password with only special characters calculates the correct score using custom weights.
    """
    password_analyzer = PasswordAnalyzer("!@#$%^&*")
    password_analyzer._PasswordAnalyzer__validators.get_analyzer_options = lambda: AnalyzerOptions(  # type: ignore
        character_weights=custom_character_weights
    )

    # 8 special characters
    expected_score = 8 * custom_character_weights[Character.SPECIAL_CHAR]
    method = getattr(password_analyzer,
                     "_PasswordAnalyzer__calculate_password_score")
    score = method()
    assert score == expected_score, f"Expected score {
        expected_score}, but got {score}"
