from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.password_analyzer import PasswordAnalyzer
from password_analyzer.validators import Validators

# * Frequently using type: ignore rule due to ruff's linting and not allowing accessing private variables


def test_password_analyzer_with_default_options():
    """
    Test that PasswordAnalyzer initializes correctly with default AnalyzerOptions.
    """
    password = "DefaultPassword123!"
    analyzer = PasswordAnalyzer(password)

    assert hasattr(
        analyzer, "_PasswordAnalyzer__password"), "PasswordAnalyzer should have a private __password attribute."
    assert hasattr(
        analyzer, "_PasswordAnalyzer__total_password_score"), "PasswordAnalyzer should have a private __total_password_score attribute."
    assert hasattr(
        analyzer, "_PasswordAnalyzer__validators"), "PasswordAnalyzer should have a private __validators attribute."

    assert analyzer._PasswordAnalyzer__password == password, "The password should match the input password."  # type: ignore
    assert analyzer._PasswordAnalyzer__total_password_score == 0, "Initial password score should be 0."  # type: ignore
    assert isinstance(analyzer._PasswordAnalyzer__validators,  # type: ignore
                      Validators), "Validators instance should be created."


def test_password_analyzer_with_none_options():
    """
    Test that PasswordAnalyzer initializes correctly when None is passed as AnalyzerOptions.
    """
    password = "PasswordWithNoneOptions"
    analyzer = PasswordAnalyzer(password, None)

    assert hasattr(
        analyzer, "_PasswordAnalyzer__password"), "PasswordAnalyzer should have a private __password attribute."
    assert hasattr(
        analyzer, "_PasswordAnalyzer__total_password_score"), "PasswordAnalyzer should have a private __total_password_score attribute."
    assert hasattr(
        analyzer, "_PasswordAnalyzer__validators"), "PasswordAnalyzer should have a private __validators attribute."

    assert analyzer._PasswordAnalyzer__password == password, "The password should match the input password."  # type: ignore
    assert analyzer._PasswordAnalyzer__total_password_score == 0, "Initial password score should be 0."  # type: ignore
    assert isinstance(analyzer._PasswordAnalyzer__validators,  # type: ignore
                      Validators), "Validators instance should be created."


def test_password_analyzer_with_custom_options():
    """
    Test that PasswordAnalyzer initializes correctly with custom AnalyzerOptions.
    """
    password = "CustomPassword!@#"
    custom_options = AnalyzerOptions(
        required_length=12,
        maximum_length=30,
        score_threshold=10,
        prohibited_characters=["!", "@", "#"],
        weak_passwords=["password123", "admin"]
    )
    analyzer = PasswordAnalyzer(password, custom_options)

    assert hasattr(
        analyzer, "_PasswordAnalyzer__password"), "PasswordAnalyzer should have a private __password attribute."
    assert hasattr(
        analyzer, "_PasswordAnalyzer__total_password_score"), "PasswordAnalyzer should have a private __total_password_score attribute."
    assert hasattr(
        analyzer, "_PasswordAnalyzer__validators"), "PasswordAnalyzer should have a private __validators attribute."

    assert analyzer._PasswordAnalyzer__password == password, "The password should match the input password."  # type: ignore
    assert analyzer._PasswordAnalyzer__total_password_score == 0, "Initial password score should be 0."  # type: ignore
    assert isinstance(analyzer._PasswordAnalyzer__validators,  # type: ignore
                      Validators), "Validators instance should be created."
    assert analyzer._PasswordAnalyzer__validators._Validators__analyzer_options == custom_options, "Custom options should be used by Validators."  # type: ignore
