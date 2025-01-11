from password_analyzer.analyzer_options import AnalyzerOptions
from password_analyzer.password_review import PasswordReview


def test_password_review_default_properties():
    """
    Test that default properties are correctly initialized when optional arguments are not provided.
    """
    password = "ExamplePassword"
    reaches_threshold = False
    review = PasswordReview(password, reaches_threshold)

    assert review.password == password, "Password should be correctly assigned."
    assert review.threshold == AnalyzerOptions(
    ).score_threshold, "Default threshold should be taken from AnalyzerOptions."
    assert review.reaches_threshold == reaches_threshold, "reaches_threshold should be correctly assigned."
    assert review.password_strength_label == "Weak", "Default password_strength_label should be 'Weak'."


def test_password_review_custom_properties():
    """
    Test that custom properties are correctly assigned.
    """
    password = "CustomPassword"
    reaches_threshold = True
    threshold = 50
    password_strength_label = "Strong"
    review = PasswordReview(password, reaches_threshold,
                            threshold, password_strength_label)

    assert review.password == password, "Password should be correctly assigned."
    assert review.threshold == threshold, "Threshold should be correctly assigned."
    assert review.reaches_threshold == reaches_threshold, "reaches_threshold should be correctly assigned."
    assert review.password_strength_label == password_strength_label, "password_strength_label should be correctly assigned."


def test_password_review_repr_fails_threshold():
    """
    Test the __repr__ method for a password that does not reach the threshold.
    """
    password = "WeakPassword"
    threshold = 20
    review = PasswordReview(password, False, threshold)

    expected_repr = f"Password: {password} does not reach the {threshold} threshold!"  # noqa
    assert repr(
        review) == expected_repr, "__repr__ output should correctly describe a password failing the threshold."


def test_password_review_repr_reaches_threshold():
    """
    Test the __repr__ method for a password that reaches the threshold.
    """
    password = "StrongPassword"
    threshold = 50
    password_strength_label = "Very Strong"
    review = PasswordReview(password, True, threshold, password_strength_label)

    expected_repr = f"Password: {password} reaches the {threshold} threshold and is {password_strength_label}"  # noqa
    assert repr(
        review) == expected_repr, "__repr__ output should correctly describe a password meeting the threshold."
