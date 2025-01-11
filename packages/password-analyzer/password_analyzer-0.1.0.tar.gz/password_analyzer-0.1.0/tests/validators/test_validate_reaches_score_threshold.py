import pytest

from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.validators import PasswordValidationError, Validators


def test_validate_reaches_score_threshold_above_threshold():
    """
    Test validate_reaches_score_threshold with a score above the threshold.
    """
    password_score = 25
    options = AnalyzerOptions(score_threshold=20)
    validators = Validators("ValidPassword", options)

    assert validators.validate_reaches_score_threshold(password_score) is True, \
        "Password score above threshold should pass validation."


def test_validate_reaches_score_threshold_exact_threshold():
    """
    Test validate_reaches_score_threshold with a score equal to the threshold.
    """
    password_score = 20
    options = AnalyzerOptions(score_threshold=20)
    validators = Validators("ValidPassword", options)

    assert validators.validate_reaches_score_threshold(password_score) is True, \
        "Password score equal to threshold should pass validation."


def test_validate_reaches_score_threshold_below_threshold():
    """
    Test validate_reaches_score_threshold with a score below the threshold.
    """
    password_score = 15
    options = AnalyzerOptions(score_threshold=20)
    validators = Validators("ValidPassword", options)

    with pytest.raises(PasswordValidationError) as exc_info:
        validators.validate_reaches_score_threshold(password_score)

    assert "Password did not reach the 20 score threshold." in str(exc_info.value), \
        "Password score below threshold should raise an error."


def test_validate_reaches_score_threshold_with_no_options():
    """
    Test validate_reaches_score_threshold when no AnalyzerOptions are provided (default options).
    """
    password_score = 15
    validators = Validators("ValidPassword", None)

    assert validators.validate_reaches_score_threshold(password_score) is True, \
        "Password with default score requirements should pass validation."
