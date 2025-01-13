def is_utf_character(char):
    """Checks if a character is a valid UTF-8 character."""
    try:
        char.encode('utf-8')
        return True
    except UnicodeEncodeError:
        return False