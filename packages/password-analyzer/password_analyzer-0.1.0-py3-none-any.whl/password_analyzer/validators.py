from typing import Optional

from password_analyzer.analyzer_options import AnalyzerOptions


class PasswordValidationError(Exception):
    """Custom exception for password validation errors."""
    pass


class Validators():
    """
    Validates passwords against various criteria such as length, regex patterns,
    prohibited characters, and scoring thresholds.

    Attributes:
    ----------
    __password : str
        The password to validate.
    __analyzer_options : AnalyzerOptions
        Configuration for validation criteria.
    """
    __password: str
    __analyzer_options: AnalyzerOptions

    def __init__(self, password: str,  options: Optional[AnalyzerOptions]) -> None:
        self.__password = password
        self.__analyzer_options = AnalyzerOptions() if not options else options

    def get_analyzer_options(self):
        return self.__analyzer_options

    def validate_length(self) -> bool:
        """
        Checks the length of password against required length.
        """
        if len(self.__password) < self.__analyzer_options.required_length:
            raise PasswordValidationError(f"Password must be at least {self.__analyzer_options.required_length} characters long.")  # noqa: F401

        if len(self.__password) > self.__analyzer_options.maximum_length:
            raise PasswordValidationError(f"Password must not exceed {self.__analyzer_options.maximum_length} characters.")  # noqa: F401

        return True

    def validate_reaches_score_threshold(self, total_password_score: int) -> bool:
        """
        Validates that password reaches at least the score threshold. 
        """
        if total_password_score < self.__analyzer_options.score_threshold:
            raise PasswordValidationError(f"Password did not reach the {self.__analyzer_options.score_threshold} score threshold.")  # noqa: F401

        return True

    def validate_prohibited_characters(self) -> bool:
        """
        Validates if password does not contain any prohibited characters.
        """
        prohibited_characters = set(
            self.__analyzer_options.prohibited_characters)

        if any(char in prohibited_characters for char in self.__password):
            raise PasswordValidationError(
                "Password contains prohibited characters.")

        return True

    def validate_weak_passwords(self) -> bool:
        """
        Validates if password does not contain an easy pattern to guess. 
        """
        for weak_password in self.__analyzer_options.weak_passwords:
            if weak_password.lower() in self.__password:
                raise PasswordValidationError(
                    "Password contains an easy pattern to guess.")

        return True
