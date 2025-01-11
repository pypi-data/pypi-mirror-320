import pytest

from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.validators import PasswordValidationError, Validators


def test_validate_prohibited_characters_without_prohibited_chars():
    """
    Test validate_prohibited_characters with a password that does not contain prohibited characters.
    """
    options = AnalyzerOptions(prohibited_characters=["0", "#"])
    validators = Validators("ValidPassword1!", options)

    assert validators.validate_prohibited_characters() is True, \
        "Password without prohibited characters should pass validation."


def test_validate_prohibited_characters_with_prohibited_characters():
    """
    Test validate_prohibited_characters with a password that contains prohibited characters.
    """
    options = AnalyzerOptions(prohibited_characters=["a", "b", "c"])
    validators = Validators("PasswordWithA!", options)

    with pytest.raises(PasswordValidationError) as exc_info:
        validators.validate_prohibited_characters()

    assert "Password contains prohibited characters." in str(exc_info.value), \
        "Password with prohibited characters should raise an error."


def test_validate_prohibited_characters_with_empty_prohibited_chars():
    """
    Test validate_prohibited_characters with an empty prohibited characters list.
    """
    options = AnalyzerOptions(prohibited_characters=[""])
    validators = Validators("NoProhibitedChars1!", options)

    assert validators.validate_prohibited_characters() is True, \
        "Password with empty prohibited characters should pass validation."


def test_validate_prohibited_characters_with_special_chars():
    """
    Test validate_prohibited_characters with a password that contains special characters in the prohibited list.
    """
    options = AnalyzerOptions(prohibited_characters=["!", "@", "#"])
    validators = Validators("PasswordWithoutSpecialChars", options)

    assert validators.validate_prohibited_characters() is True, \
        "Password without prohibited special characters should pass validation."

    validators = Validators("PasswordWith!Special#", options)

    with pytest.raises(PasswordValidationError) as exc_info:
        validators.validate_prohibited_characters()

    assert "Password contains prohibited characters." in str(exc_info.value), \
        "Password with prohibited special characters should raise an error."
