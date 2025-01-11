from unittest.mock import MagicMock

import pytest

from password_analyzer.password_analyzer import (
    PasswordAnalyzer,
    PasswordValidationError,
)


@pytest.fixture
def password_analyzer() -> PasswordAnalyzer:
    """Fixture for initializing a PasswordAnalyzer instance."""
    return PasswordAnalyzer("TestPassword123!")


def test_suggest_improvements_valid_password(password_analyzer: PasswordAnalyzer):
    """
    Test suggest_improvements with a valid password (no suggestions required).
    """
    # Mock dependencies
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock()  # type:ignore
    password_analyzer.get_password_review = MagicMock(
        return_value=MagicMock(password_strength_label="Strong")
    )

    # Call the method
    suggestions = password_analyzer.suggest_improvements()

    # Assert no suggestions
    assert suggestions == ["Your password is Strong!"]


def test_suggest_improvements_length_issue(password_analyzer: PasswordAnalyzer):
    """
    Test suggest_improvements when the password length is invalid.
    """
    # Mock dependencies
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock(  # type:ignore
        side_effect=PasswordValidationError(
            "Password must be at least 8 characters long")
    )
    password_analyzer._PasswordAnalyzer__validators.get_analyzer_options = MagicMock(  # type:ignore
        return_value=MagicMock(required_length=8, maximum_length=32)
    )
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock()  # type:ignore
    password_analyzer.get_password_review = MagicMock(
        return_value=MagicMock(password_strength_label="Weak")
    )

    # Call the method
    suggestions = password_analyzer.suggest_improvements()

    # Assert suggestions include length improvement
    assert "Increase your password length to be minimum 8 characters long" in suggestions


def test_suggest_improvements_weak_patterns(password_analyzer: PasswordAnalyzer):
    """
    Test suggest_improvements when the password contains weak patterns.
    """
    # Mock dependencies
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock(  # type:ignore
        side_effect=PasswordValidationError("Weak password patterns found")
    )
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock()  # type:ignore
    password_analyzer.get_password_review = MagicMock(
        return_value=MagicMock(password_strength_label="Fair")
    )

    # Call the method
    suggestions = password_analyzer.suggest_improvements()

    # Assert suggestions include removing weak patterns
    assert "Remove common patterns like qwerty, 1234 and so on..." in suggestions


def test_suggest_improvements_prohibited_characters(password_analyzer: PasswordAnalyzer):
    """
    Test suggest_improvements when the password contains prohibited characters.
    """
    # Mock dependencies
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock(  # type:ignore
        side_effect=PasswordValidationError("Prohibited characters found")
    )
    password_analyzer.get_password_review = MagicMock(
        return_value=MagicMock(password_strength_label="Weak")
    )

    # Call the method
    suggestions = password_analyzer.suggest_improvements()

    # Assert suggestions include prohibited character removal
    assert (
        "Your password contains prohibited characters defined earlier. Remove them!"
        in suggestions
    )


def test_suggest_improvements_multiple_issues(password_analyzer: PasswordAnalyzer):
    """
    Test suggest_improvements when multiple issues exist with the password.
    """
    # Mock dependencies
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock(  # type:ignore
        side_effect=PasswordValidationError(
            "Password must be at least 8 characters long")
    )
    password_analyzer._PasswordAnalyzer__validators.get_analyzer_options = MagicMock(  # type:ignore
        return_value=MagicMock(required_length=8, maximum_length=32)
    )
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock(  # type:ignore
        side_effect=PasswordValidationError("Weak password patterns found")
    )
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock(  # type:ignore
        side_effect=PasswordValidationError("Prohibited characters found")
    )
    password_analyzer.get_password_review = MagicMock(
        return_value=MagicMock(password_strength_label="Fair")
    )

    # Call the method
    suggestions = password_analyzer.suggest_improvements()

    # Assert all suggestions are present
    assert "Increase your password length to be minimum 8 characters long" in suggestions
    assert "Remove common patterns like qwerty, 1234 and so on..." in suggestions
    assert (
        "Your password contains prohibited characters defined earlier. Remove them!"
        in suggestions
    )
    assert "Your password isn't as good as it can be. Strengthen it using special characters like !, $ etc." in suggestions
