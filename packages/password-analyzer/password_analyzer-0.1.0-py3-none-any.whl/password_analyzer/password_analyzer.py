from typing import Optional

from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.constants import Character
from password_analyzer.password_review import (
    PasswordReview,
    get_password_strength_label,
)
from password_analyzer.validators import PasswordValidationError, Validators


class PasswordAnalyzer():
    """
    Analyzes the strength of passwords based on complexity rules, such as
    character diversity, length, and common weaknesses.

    Attributes:
    ----------
    __password : str
        The password to analyze.
    __total_password_score : int
        The strength score of the password.
    __validators: Validators settings for the analyzer
    """

    __password: str
    __total_password_score: int
    __validators: Validators

    def __init__(self, password: str, analyzer_options: Optional[AnalyzerOptions] = AnalyzerOptions()):
        self.__password = password
        self.__total_password_score = 0
        self.__validators = Validators(self.__password, analyzer_options)

    def __calculate_password_score(self):
        """
        Calculates the password score.
        """
        score = 0
        character_weights = self.__validators.get_analyzer_options().character_weights

        for char in self.__password:
            if char.islower():
                score += character_weights[Character.LOWERCASE]
            elif char.isupper():
                score += character_weights[Character.UPPERCASE]
            elif char.isdigit():
                score += character_weights[Character.NUMBER]
            else:
                # The character is special
                score += character_weights[Character.SPECIAL_CHAR]

        return score

    def __calculate_and_validate_password_strength(self) -> None:
        """
        Validates password against possible weaknesses.
        """
        self.__validators.validate_length()
        self.__validators.validate_weak_passwords()
        self.__validators.validate_prohibited_characters()

        self.__total_password_score = self.__calculate_password_score()

        self.__validators.validate_reaches_score_threshold(
            self.__total_password_score)

    def is_password_strong_enough(self) -> bool:
        if self.__total_password_score == 0:
            try:
                self.__calculate_and_validate_password_strength()
                return True
            except PasswordValidationError:
                return False

        return True

    def get_password_review(self) -> PasswordReview:
        is_password_strong_enough = self.is_password_strong_enough()

        password_strength_label = get_password_strength_label(
            self.__total_password_score
        )
        threshold = self.__validators.get_analyzer_options().score_threshold

        return PasswordReview(
            password=self.__password,
            reaches_threshold=is_password_strong_enough,
            threshold=threshold,
            password_strength_label=password_strength_label
        )

    def suggest_improvements(self) -> list[str]:
        """
        Suggests improvements to enhance password strength and comply with validation rules.
        """
        suggested_improvements: list[str] = []

        try:
            self.__validators.validate_length()
        except PasswordValidationError as e:
            if str(e).startswith("Password must be at least"):
                suggested_improvements.append(f"Increase your password length to be minimum {self.__validators.get_analyzer_options().required_length} characters long")  # noqa
            else:
                suggested_improvements.append(f"Reduce your password length to be maximum {self.__validators.get_analyzer_options().maximum_length} characters long")  # noqa

        try:
            self.__validators.validate_weak_passwords()
        except PasswordValidationError:
            suggested_improvements.append(
                "Remove common patterns like qwerty, 1234 and so on...")

        try:
            self.__validators.validate_prohibited_characters()
        except PasswordValidationError:
            suggested_improvements.append(
                "Your password contains prohibited characters defined earlier. Remove them!")

        password_strength_label = self.get_password_review().password_strength_label

        if (password_strength_label == "Weak" or password_strength_label == "Fair"):
            suggested_improvements.append(
                "Your password isn't as good as it can be. Strengthen it using special characters like !, $ etc.")

        if len(suggested_improvements) == 0:
            return [f"Your password is {password_strength_label}!"]

        return suggested_improvements
