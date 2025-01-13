from multiprocessing import Pool, cpu_count
from .utils import is_utf_character

def _filter_chunk(chunk):
    """Filters non-UTF characters from a chunk of text."""
    return ''.join(c for c in chunk if is_utf_character(c))

class UTFMultiprocessingHandler:
    """Handles multiprocessing-based filtering."""

    @staticmethod
    def filter_with_multiprocessing(text):
        chunk_size = max(1, len(text) // cpu_count())  # Divide text into chunks
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        
        with Pool(cpu_count()) as pool:
            filtered_chunks = pool.map(_filter_chunk, chunks)
        
        return ''.join(filtered_chunks)