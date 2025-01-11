from password_analyzer.constants import Character


def test_character_enum_exists():
    """
    Test that the Character enum exists and has all defined members.
    """
    assert Character is not None, "Character enum does not exist."
    assert hasattr(
        Character, 'LOWERCASE'), "LOWERCASE is not defined in Character enum."
    assert hasattr(
        Character, 'UPPERCASE'), "UPPERCASE is not defined in Character enum."
    assert hasattr(
        Character, 'NUMBER'), "NUMBER is not defined in Character enum."
    assert hasattr(
        Character, 'SPECIAL_CHAR'), "SPECIAL_CHAR is not defined in Character enum."


def test_character_enum_values():
    """
    Test that Character enum values are assigned correctly.
    """
    assert Character.LOWERCASE.value == 1, "LOWERCASE does not have the correct value."
    assert Character.UPPERCASE.value == 2, "UPPERCASE does not have the correct value."
    assert Character.NUMBER.value == 3, "NUMBER does not have the correct value."
    assert Character.SPECIAL_CHAR.value == 4, "SPECIAL_CHAR does not have the correct value."


def test_character_enum_uniqueness():
    """
    Test that Character enum members are distinct if intended, or flagged for shared values.
    """
    enum_values = [member.name for member in Character]
    duplicates = [
        value for value in enum_values if enum_values.count(value) > 1]
    assert len(duplicates) == 0, (
        "Enum values are not unique, which may lead to unexpected behavior."
    )


def test_character_enum_member_access():
    """
    Test accessing members of the Character enum.
    """
    assert Character['LOWERCASE'] == Character.LOWERCASE, "Member access via string is incorrect."
    assert Character['UPPERCASE'] == Character.UPPERCASE, "Member access via string is incorrect."
    assert Character['NUMBER'] == Character.NUMBER, "Member access via string is incorrect."
    assert Character['SPECIAL_CHAR'] == Character.SPECIAL_CHAR, "Member access via string is incorrect."


def test_character_enum_iteration():
    """
    Test that Character enum can be iterated over.
    """
    members = list(Character)
    assert len(members) == 4, "Character enum does not contain all members."
    assert Character.LOWERCASE in members, "LOWERCASE is missing from iteration."
    assert Character.UPPERCASE in members, "UPPERCASE is missing from iteration."
    assert Character.NUMBER in members, "NUMBER is missing from iteration."
    assert Character.SPECIAL_CHAR in members, "SPECIAL_CHAR is missing from iteration."
