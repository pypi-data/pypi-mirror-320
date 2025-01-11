import pytest

from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.validators import PasswordValidationError, Validators


def test_validate_length_with_valid_length():
    """
    Test validate_length method with a password of valid length.
    """
    password = "ValidPassword"
    options = AnalyzerOptions(required_length=8, maximum_length=20)
    validators = Validators(password, options)

    assert validators.validate_length(
    ) is True, "Password with valid length should pass validation."


def test_validate_length_too_short():
    """
    Test validate_length method with a password that is too short.
    """
    password = "Short"
    options = AnalyzerOptions(required_length=8, maximum_length=20)
    validators = Validators(password, options)

    with pytest.raises(PasswordValidationError) as exc_info:
        validators.validate_length()

    assert "Password must be at least 8 characters long." in str(exc_info.value), \
        "Password shorter than required length should raise an error."


def test_validate_length_too_long():
    """
    Test validate_length method with a password that exceeds the maximum length.
    """
    password = "ThisPasswordIsWayTooLongForTheValidator"
    options = AnalyzerOptions(required_length=8, maximum_length=20)
    validators = Validators(password, options)

    with pytest.raises(PasswordValidationError) as exc_info:
        validators.validate_length()

    assert "Password must not exceed 20 characters." in str(exc_info.value), \
        "Password longer than maximum length should raise an error."


def test_validate_length_at_minimum_length():
    """
    Test validate_length method with a password that is exactly at the minimum required length.
    """
    password = "MinLength"
    options = AnalyzerOptions(required_length=9, maximum_length=20)
    validators = Validators(password, options)

    assert validators.validate_length(
    ) is True, "Password at the exact minimum length should pass validation."


def test_validate_length_at_maximum_length():
    """
    Test validate_length method with a password that is exactly at the maximum allowed length.
    """
    password = "MaxLengthPassword"
    options = AnalyzerOptions(required_length=8, maximum_length=18)
    validators = Validators(password, options)

    assert validators.validate_length(
    ) is True, "Password at the exact maximum length should pass validation."


def test_validate_length_with_no_options():
    """
    Test validate_length method when no AnalyzerOptions are provided (default options).
    """
    password = "DefaultValid"
    validators = Validators(password, None)

    assert validators.validate_length(
    ) is True, "Password with default length requirements should pass validation."
