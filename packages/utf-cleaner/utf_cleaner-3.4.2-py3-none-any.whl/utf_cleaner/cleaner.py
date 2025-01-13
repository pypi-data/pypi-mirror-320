from .validator import UTFValidator
from .logger import UTFLogger
from .utils import is_utf_character
from .multiprocessing_handler import UTFMultiprocessingHandler

class UTFStringCleaner:
    """A class for removing non-UTF characters."""

    def __init__(self, use_multiprocessing=False):
        self.use_multiprocessing = use_multiprocessing

    def clean(self, text):
        """Removes non-UTF characters from the input text."""
        UTFValidator.validate_input(text)  # Validate input

        if self.use_multiprocessing:
            cleaned_text = UTFMultiprocessingHandler.filter_with_multiprocessing(text)
        else:
            cleaned_text = ''.join(c for c in text if is_utf_character(c))

        UTFLogger.log_removal(text, cleaned_text)  # Log removed characters
        return cleaned_text