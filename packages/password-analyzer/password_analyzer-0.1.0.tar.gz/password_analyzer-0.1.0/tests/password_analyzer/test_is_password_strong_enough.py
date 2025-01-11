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


def test_is_password_strong_enough_score_zero_valid_password(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that a password with a score of 0 is calculated as strong when it passes validation.
    """
    # Mock the private calculate_and_validate_password_strength method to not raise an exception
    password_analyzer._PasswordAnalyzer__calculate_and_validate_password_strength = MagicMock()  # type:ignore

    # Ensure the initial total score is 0
    password_analyzer._PasswordAnalyzer__total_password_score = 0  # type:ignore

    assert password_analyzer.is_password_strong_enough() is True
    password_analyzer._PasswordAnalyzer__calculate_and_validate_password_strength.assert_called_once()  # type:ignore


def test_is_password_strong_enough_score_zero_invalid_password(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that a password with a score of 0 is calculated as weak when validation fails.
    """
    # Mock the private calculate_and_validate_password_strength method to raise an exception
    password_analyzer._PasswordAnalyzer__calculate_and_validate_password_strength = MagicMock(  # type:ignore
        side_effect=PasswordValidationError(
            "Password does not meet the required criteria.")
    )

    # Ensure the initial total score is 0
    password_analyzer._PasswordAnalyzer__total_password_score = 0  # type:ignore

    assert password_analyzer.is_password_strong_enough() is False
    password_analyzer._PasswordAnalyzer__calculate_and_validate_password_strength.assert_called_once()  # type:ignore


def test_is_password_strong_enough_score_non_zero(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test that a password with a non-zero score is considered strong without recalculating.
    """
    # Set the total password score to a non-zero value
    password_analyzer._PasswordAnalyzer__total_password_score = 20  # type:ignore

    # Ensure the private method is not called
    password_analyzer._PasswordAnalyzer__calculate_and_validate_password_strength = MagicMock()  # type:ignore

    assert password_analyzer.is_password_strong_enough() is True
    password_analyzer._PasswordAnalyzer__calculate_and_validate_password_strength.assert_not_called()  # type:ignore
