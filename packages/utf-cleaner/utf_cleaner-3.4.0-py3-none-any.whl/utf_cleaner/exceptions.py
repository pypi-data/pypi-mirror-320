class UTFCleaningError(Exception):
    """Base exception for UTF cleaning errors."""
    pass


class InvalidInputError(UTFCleaningError):
    """Raised when input is not a valid string."""
    def __init__(self, message="Input must be a string."):
        super().__init__(message)