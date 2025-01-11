import pytest

from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.validators import PasswordValidationError, Validators


def test_validate_weak_passwords_without_weak_patterns():
    """
    Test validate_weak_passwords with a password that does not contain any weak patterns.
    """
    options = AnalyzerOptions(weak_passwords=["123456", "password", "qwerty"])
    validators = Validators("StrongPass1!", options)

    assert validators.validate_weak_passwords() is True, \
        "Password without weak patterns should pass validation."


def test_validate_weak_passwords_with_weak_patterns():
    """
    Test validate_weak_passwords with a password that contains a weak pattern.
    """
    options = AnalyzerOptions(weak_passwords=["123456", "password", "qwerty"])
    validators = Validators("password123", options)

    with pytest.raises(PasswordValidationError) as exc_info:
        validators.validate_weak_passwords()

    assert "Password contains an easy pattern to guess." in str(exc_info.value), \
        "Password with a weak pattern should raise an error."


def test_validate_weak_passwords_with_multiple_patterns():
    """
    Test validate_weak_passwords with a password that contains multiple weak patterns.
    """
    options = AnalyzerOptions(weak_passwords=["123456", "password", "qwerty"])
    validators = Validators("123456password", options)

    with pytest.raises(PasswordValidationError) as exc_info:
        validators.validate_weak_passwords()

    assert "Password contains an easy pattern to guess." in str(exc_info.value), \
        "Password with multiple weak patterns should raise an error."


def test_validate_weak_passwords_with_empty_weak_patterns():
    """
    Test validate_weak_passwords with an empty weak patterns list.
    """
    options = AnalyzerOptions(weak_passwords=[])
    validators = Validators("ValidString", options)

    assert validators.validate_weak_passwords() is True, \
        "Password with an empty weak patterns list should pass validation."
