from password_analyzer.password_analyzer import get_password_strength_label


def test_get_password_strength_label_weak():
    """
    Test that scores <= 10 return 'Weak'.
    """
    for score in range(0, 11):
        assert get_password_strength_label(score) == "Weak", f"Score {
            score} should return 'Weak'"


def test_get_password_strength_label_fair():
    """
    Test that scores > 10 and <= 30 return 'Fair'.
    """
    for score in range(11, 31):
        assert get_password_strength_label(score) == "Fair", f"Score {
            score} should return 'Fair'"


def test_get_password_strength_label_good():
    """
    Test that scores > 30 and <= 50 return 'Good'.
    """
    for score in range(31, 51):
        assert get_password_strength_label(score) == "Good", f"Score {
            score} should return 'Good'"


def test_get_password_strength_label_strong():
    """
    Test that scores > 50 and <= 70 return 'Strong'.
    """
    for score in range(51, 71):
        assert get_password_strength_label(score) == "Strong", f"Score {
            score} should return 'Strong'"


def test_get_password_strength_label_very_strong():
    """
    Test that scores > 70 return 'Very Strong'.
    """
    for score in range(71, 101):
        assert get_password_strength_label(score) == "Very Strong", f"Score {
            score} should return 'Very Strong'"


def test_get_password_strength_label_very_strong_for_high_values():
    assert get_password_strength_label(
        150) == "Very Strong", "Score 150 should return Very Strong"
    assert get_password_strength_label(
        300) == "Very Strong", "Score 300 should return Very Strong"
