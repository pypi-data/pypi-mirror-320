import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class UTFLogger:
    """Logger for tracking character removals."""
    
    @staticmethod
    def log_removal(original, cleaned):
        removed_chars = set(original) - set(cleaned)
        if removed_chars:
            logging.info(f"Removed non-UTF characters: {''.join(removed_chars)}")