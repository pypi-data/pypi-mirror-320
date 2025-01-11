from .exceptions import InvalidInputError

class UTFValidator:
    """Validator for UTF-8 strings."""
    
    @staticmethod
    def validate_input(text):
        if not isinstance(text, str):
            raise InvalidInputError()