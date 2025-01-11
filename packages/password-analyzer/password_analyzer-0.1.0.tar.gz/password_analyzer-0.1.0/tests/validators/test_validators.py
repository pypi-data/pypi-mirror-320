from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.constants import WEAK_PASSWORD_PATTERNS
from password_analyzer.validators import Validators


def test_validators_initialization_with_default_options():
    """
    Test that Validators can be initialized with default AnalyzerOptions.
    """
    password = "TestPassword123!"
    validators = Validators(password, None)

    assert validators is not None, "Validators instance should be created successfully."
    assert hasattr(
        validators, "_Validators__password"), "Validators should have a private password attribute."
    assert hasattr(
        validators, "_Validators__analyzer_options"), "Validators should have a private analyzer_options attribute."


def test_validators_initialization_with_custom_options():
    """
    Test that Validators can be initialized with custom AnalyzerOptions.
    """
    password = "CustomPassword!@#"
    custom_options = AnalyzerOptions(required_length=12, maximum_length=50)
    validators = Validators(password, custom_options)

    assert validators is not None, "Validators instance should be created successfully."
    assert hasattr(
        validators, "_Validators__password"), "Validators should have a private password attribute."
    assert hasattr(
        validators, "_Validators__analyzer_options"), "Validators should have a private analyzer_options attribute."


def test_validators_empty_password():
    """
    Test that Validators can handle an empty password.
    """
    password = ""
    validators = Validators(password, None)

    assert validators is not None, "Validators instance should be created successfully."
    assert hasattr(
        validators, "_Validators__password"), "Validators should have a private password attribute."


def test_validators_none_options():
    """
    Test that Validators can handle None as AnalyzerOptions.
    """
    password = "ValidPassword"
    validators = Validators(password, None)

    assert validators is not None, "Validators instance should be created successfully."
    assert hasattr(
        validators, "_Validators__analyzer_options"), "Validators should have a private analyzer_options attribute."


def test_validators_custom_options_properties():
    """
    Test that custom AnalyzerOptions properties are respected.
    """
    password = "AnotherCustomPassword"

    custom_options = AnalyzerOptions(
        required_length=10,
        maximum_length=30,
        score_threshold=15,
        prohibited_characters=["!"],
        weak_passwords=["password123", "admin"]
    )

    validators = Validators(password, custom_options)

    assert hasattr(
        validators, "_Validators__analyzer_options"), "Validators should have a private analyzer_options attribute."
    assert hasattr(
        custom_options, "required_length"), "AnalyzerOptions should have a required_length property."
    assert hasattr(
        custom_options, "maximum_length"), "AnalyzerOptions should have a maximum_length property."
    assert hasattr(
        custom_options, "prohibited_characters"), "AnalyzerOptions should have a prohibited_characters property."
    assert hasattr(
        custom_options, "weak_passwords"), "AnalyzerOptions should have a weak_passwords property."


def test_validators_custom_options_properties_values():
    """
    Test that custom AnalyzerOptions properties are correctly set and respected.
    """
    password = "AnotherCustomPassword"
    passwords = WEAK_PASSWORD_PATTERNS + ["password123", "admin"]

    custom_options = AnalyzerOptions(
        required_length=10,
        maximum_length=30,
        score_threshold=15,
        prohibited_characters=["!"],
        weak_passwords=["password123", "admin"]
    )

    validators = Validators(password, custom_options)

    # Check that the custom options are correctly set in the Validators instance
    assert hasattr(
        validators, "_Validators__analyzer_options"), "Validators should have a private analyzer_options attribute."
    analyzer_options: AnalyzerOptions | None = getattr(
        validators, "_Validators__analyzer_options")

    assert analyzer_options is not None
    print(analyzer_options.prohibited_characters)

    assert analyzer_options.required_length == 10, \
        "The required_length property should be set to the custom value of 10."
    assert analyzer_options.maximum_length == 30, \
        "The maximum_length property should be set to the custom value of 30."
    assert analyzer_options.score_threshold == 15, \
        "The score_threshold property should be set to the custom value of 15."
    assert analyzer_options.prohibited_characters == ["!"], \
        "The prohibited_characters property should be set to the custom value [' ', '!']."
    assert analyzer_options.weak_passwords == passwords, "The weak_passwords property should be set to the custom value ['password123', 'admin']."
