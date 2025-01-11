from typing import Literal, Optional

from password_analyzer.analyzer_options import AnalyzerOptions

PASSWORD_STRENGTH_LABEL = Literal["Weak",
                                  "Fair", "Good", "Strong", "Very Strong"]


def get_password_strength_label(password_score: int) -> PASSWORD_STRENGTH_LABEL:
    """
    Maps the total password score to a qualitative strength label.

    Returns:
    --------
    PASSWORD_STRENGTH_LABEL: The strength label for the password.
    """
    if password_score <= 10:
        return "Weak"
    elif password_score <= 30:
        return "Fair"
    elif password_score <= 50:
        return "Good"
    elif password_score <= 70:
        return "Strong"

    return "Very Strong"


class PasswordReview():
    password: str
    threshold: int
    reaches_threshold: bool
    password_strength_label: PASSWORD_STRENGTH_LABEL

    def __init__(self, password: str, reaches_threshold: bool, threshold: Optional[int] = None, password_strength_label: Optional[PASSWORD_STRENGTH_LABEL] = None) -> None:
        self.password = password
        self.threshold = threshold if threshold else AnalyzerOptions().score_threshold
        self.reaches_threshold = reaches_threshold
        self.password_strength_label = password_strength_label if password_strength_label else "Weak"

    def __repr__(self) -> str:
        if not self.reaches_threshold:
            return f"Password: {self.password} does not reach the {self.threshold} threshold!"

        return f"Password: {self.password} reaches the {self.threshold} threshold and is {self.password_strength_label}"
