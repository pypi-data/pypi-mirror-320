# morph_extractor/token_utils.py

import logging

logger = logging.getLogger(__name__)

try:
    import tiktoken
    ENCODER = tiktoken.get_encoding("cl100k_base")  # Use the same encoder for tokenization
except ImportError:
    logger.warning("tiktoken not installed. Falling back to naive token counting.")
    ENCODER = None

def get_num_tokens(text: str) -> int:
    """
    Use tiktoken if available, else fallback to whitespace-based counting.
    """
    if ENCODER:
        return len(ENCODER.encode(text))
    return len(text.split())

def chunk_text_by_tokens(text: str, max_tokens: int) -> list[str]:
    """
    Split the text into multiple chunks not exceeding 'max_tokens' each.
    """
    if ENCODER:
        tokens = ENCODER.encode(text)
        chunks = []
        current_tokens = []

        for token in tokens:
            if len(current_tokens) + 1 > max_tokens:
                chunks.append(ENCODER.decode(current_tokens))
                current_tokens = [token]
            else:
                current_tokens.append(token)
        if current_tokens:
            chunks.append(ENCODER.decode(current_tokens))
        return chunks
    else:
        # Naive fallback
        words = text.split()
        chunks = []
        current_chunk = []
        for word in words:
            if len(current_chunk) + 1 > max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
            else:
                current_chunk.append(word)
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks





'''# morph_extractor/token_utils.py

import logging

logger = logging.getLogger(__name__)

try:
    import tiktoken
    ENCODER = tiktoken.get_encoding("cl100k_base")
except ImportError:
    logger.warning("tiktoken not installed. Falling back to naive token counting.")
    ENCODER = None

def get_num_tokens(text: str) -> int:
    """
    Use tiktoken if available, else fallback to whitespace-based counting.
    """
    if ENCODER:
        return len(ENCODER.encode(text))
    return len(text.split())

def chunk_text_by_tokens(text: str, max_tokens: int) -> list[str]:
    """
    Split the text into multiple chunks not exceeding 'max_tokens' each.
    """
    if ENCODER:
        tokens = ENCODER.encode(text)
        chunks = []
        current_tokens = []

        for token in tokens:
            if len(current_tokens) + 1 > max_tokens:
                chunks.append(ENCODER.decode(current_tokens))
                current_tokens = [token]
            else:
                current_tokens.append(token)
        if current_tokens:
            chunks.append(ENCODER.decode(current_tokens))
        return chunks
    else:
        # Naive fallback
        words = text.split()
        chunks = []
        current_chunk = []
        for word in words:
            if len(current_chunk) + 1 > max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
            else:
                current_chunk.append(word)
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks
'''