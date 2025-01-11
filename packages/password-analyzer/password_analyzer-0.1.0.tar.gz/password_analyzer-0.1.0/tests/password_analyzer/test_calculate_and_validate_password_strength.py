from unittest.mock import MagicMock

import pytest

from password_analyzer.password_analyzer import (
    PasswordAnalyzer,
    PasswordValidationError,
)


@pytest.fixture
def password_analyzer() -> PasswordAnalyzer:
    """
    Fixture to provide a PasswordAnalyzer instance with a default password.
    """
    return PasswordAnalyzer("ValidPassword123!")


def test_calculate_and_validate_strength_success(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that the method successfully validates a strong password.
    """
    # Mock validators to ensure no exceptions are raised
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock()  # type: ignore
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock()  # type: ignore
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock()  # type: ignore
    password_analyzer._PasswordAnalyzer__validators.validate_reaches_score_threshold = MagicMock()  # type: ignore

    method = getattr(
        password_analyzer, "_PasswordAnalyzer__calculate_and_validate_password_strength")

    # Run the method and verify no exceptions occur
    try:
        method()
        assert password_analyzer._PasswordAnalyzer__total_password_score > 0, (  # type: ignore
            "Password score should be calculated and greater than 0 for a valid password."
        )
    except Exception as e:
        pytest.fail(f"Unexpected exception raised: {e}")


def test_calculate_and_validate_strength_invalid_length(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that the method raises a PasswordValidationError for invalid length.
    """
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock(  # type: ignore
        side_effect=PasswordValidationError(
            "Password must be at least 8 characters.")
    )

    method = getattr(
        password_analyzer, "_PasswordAnalyzer__calculate_and_validate_password_strength")

    with pytest.raises(PasswordValidationError, match="Password must be at least 8 characters."):
        method()


def test_calculate_and_validate_strength_weak_password(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that the method raises a PasswordValidationError for weak passwords.
    """
    error_message = "Password contains an easy pattern to guess."
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock(  # type: ignore
        side_effect=PasswordValidationError(error_message)
    )

    method = getattr(
        password_analyzer, "_PasswordAnalyzer__calculate_and_validate_password_strength")

    with pytest.raises(PasswordValidationError, match=error_message):
        method()


def test_calculate_and_validate_strength_prohibited_characters(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that the method raises a PasswordValidationError for prohibited characters.
    """
    # Mock earlier validators to ensure they don't raise exceptions
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock()  # type:ignore
    # Mock prohibited characters validator to raise an exception
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock(  # type:ignore
        side_effect=PasswordValidationError(
            "Password contains prohibited characters.")
    )

    method = getattr(
        password_analyzer, "_PasswordAnalyzer__calculate_and_validate_password_strength")

    with pytest.raises(PasswordValidationError, match="Password contains prohibited characters."):
        method()


def test_calculate_and_validate_strength_below_threshold(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that the method raises a PasswordValidationError for not reaching the score threshold.
    """
    # Mock earlier validators to ensure they don't raise exceptions
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock()  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock()  # type:ignore
    # Mock the score calculation to return a low value
    password_analyzer._PasswordAnalyzer__calculate_password_score = MagicMock(  # type:ignore
        return_value=5)
    # Mock score threshold validation to raise an exception
    password_analyzer._PasswordAnalyzer__validators.validate_reaches_score_threshold = MagicMock(  # type:ignore
        side_effect=PasswordValidationError(
            "Password score does not meet the required threshold.")
    )

    method = getattr(
        password_analyzer, "_PasswordAnalyzer__calculate_and_validate_password_strength")

    with pytest.raises(PasswordValidationError, match="Password score does not meet the required threshold."):
        method()


def test_calculate_and_validate_strength_score_updated(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that the password score is correctly updated during validation.
    """
    # Mock the score calculation and all validators
    password_analyzer._PasswordAnalyzer__calculate_password_score = MagicMock(  # type: ignore
        return_value=42)
    password_analyzer._PasswordAnalyzer__validators.validate_reaches_score_threshold = MagicMock()  # type: ignore
    password_analyzer._PasswordAnalyzer__validators.validate_length = MagicMock()  # type: ignore
    password_analyzer._PasswordAnalyzer__validators.validate_prohibited_characters = MagicMock()  # type: ignore
    password_analyzer._PasswordAnalyzer__validators.validate_weak_passwords = MagicMock()  # type: ignore

    method = getattr(
        password_analyzer, "_PasswordAnalyzer__calculate_and_validate_password_strength")
    method()

    assert password_analyzer._PasswordAnalyzer__total_password_score == 42, (  # type: ignore
        f"Expected password score to be 42, but got {
            password_analyzer._PasswordAnalyzer__total_password_score}."  # type:ignore
    )
