from unittest.mock import MagicMock

import pytest

from password_analyzer.password_analyzer import (
    PasswordAnalyzer,
)
from password_analyzer.password_review import PasswordReview


@pytest.fixture
def password_analyzer() -> PasswordAnalyzer:
    """Fixture for initializing a PasswordAnalyzer instance."""
    return PasswordAnalyzer("TestPassword123!")


def test_get_password_review_valid_password(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test get_password_review with a valid password.
    """
    # Mock dependencies
    password_analyzer.is_password_strong_enough = MagicMock(return_value=True)
    password_analyzer._PasswordAnalyzer__total_password_score = 50  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.get_analyzer_options = MagicMock(  # type:ignore
        return_value=MagicMock(score_threshold=40)
    )

    # Call the method
    review = password_analyzer.get_password_review()

    # Assert the results
    assert isinstance(review, PasswordReview)
    assert review.password == "TestPassword123!"
    assert review.reaches_threshold is True
    assert review.threshold == 40
    assert review.password_strength_label == "Good"


def test_get_password_review_weak_password(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test get_password_review with a weak password.
    """
    # Mock dependencies
    password_analyzer.is_password_strong_enough = MagicMock(return_value=False)
    password_analyzer._PasswordAnalyzer__total_password_score = 5  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.get_analyzer_options = MagicMock(  # type:ignore
        return_value=MagicMock(score_threshold=40)
    )

    # Call the method
    review = password_analyzer.get_password_review()

    # Assert the results
    assert isinstance(review, PasswordReview)
    assert review.password == "TestPassword123!"
    assert review.reaches_threshold is False
    assert review.threshold == 40
    assert review.password_strength_label == "Weak"


def test_get_password_review_with_custom_threshold(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test get_password_review with a custom threshold.
    """
    # Mock dependencies
    password_analyzer.is_password_strong_enough = MagicMock(return_value=True)
    password_analyzer._PasswordAnalyzer__total_password_score = 70  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.get_analyzer_options = MagicMock(  # type:ignore
        return_value=MagicMock(score_threshold=60)
    )

    # Call the method
    review = password_analyzer.get_password_review()

    # Assert the results
    assert isinstance(review, PasswordReview)
    assert review.password == "TestPassword123!"
    assert review.reaches_threshold is True
    assert review.threshold == 60
    assert review.password_strength_label == "Strong"


def test_get_password_review_handles_exceptions(password_analyzer: PasswordAnalyzer) -> None:
    """
    Test get_password_review when is_password_strong_enough returns False due to failed validation.
    """
    # Mock dependencies
    password_analyzer.is_password_strong_enough = MagicMock(return_value=False)
    password_analyzer._PasswordAnalyzer__total_password_score = 0  # type:ignore
    password_analyzer._PasswordAnalyzer__validators.get_analyzer_options = MagicMock(  # type:ignore
        return_value=MagicMock(score_threshold=40)
    )

    # Call the method
    review = password_analyzer.get_password_review()

    # Assert the results
    assert isinstance(review, PasswordReview)
    assert review.password == "TestPassword123!"
    assert review.reaches_threshold is False
    assert review.threshold == 40
    assert review.password_strength_label == "Weak"
