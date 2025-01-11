from password_analyzer.constants import DEFAULT_CHARACTER_WEIGHTS, Character


def test_default_character_weights():
    """
    Test if DEFAULT_CHARACTER_WEIGHTS contains the expected character weights.
    """
    expected_weights = {
        Character.LOWERCASE: 1,
        Character.UPPERCASE: 2,
        Character.NUMBER: 3,
        Character.SPECIAL_CHAR: 4,
    }

    for char_type, expected_weight in expected_weights.items():
        assert DEFAULT_CHARACTER_WEIGHTS[char_type] == expected_weight, (
            f"Weight for {char_type.name} is incorrect. "
            f"Expected: {expected_weight}, Got: {
                DEFAULT_CHARACTER_WEIGHTS[char_type]}"
        )


def test_character_weights_keys():
    """
    Test if all expected Character types are keys in DEFAULT_CHARACTER_WEIGHTS.
    """
    expected_keys = {Character.LOWERCASE, Character.UPPERCASE,
                     Character.NUMBER, Character.SPECIAL_CHAR}
    actual_keys = set(DEFAULT_CHARACTER_WEIGHTS.keys())
    assert actual_keys == expected_keys, (
        f"Expected keys: {expected_keys}, Actual keys: {actual_keys}"
    )


def test_character_weights_values():
    """
    Test if DEFAULT_CHARACTER_WEIGHTS contains only integer values.
    """
    for weight in DEFAULT_CHARACTER_WEIGHTS.values():
        assert isinstance(weight, int), f"Weight should be an integer, got: {
            type(weight)}"
