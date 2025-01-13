"""
Utility
"""

import hashlib

def generate_file_hash(input_string: str) -> str:
    """
    Generate a SHA-256 hash for the given input string to be used as a file name.

    Args:
        input_string (str): The input string to hash.

    Returns:
        str: A hexadecimal string representation of the hash.
    """
    if not input_string:
        raise ValueError("Input string cannot be empty.")
    
    # Calculate the SHA-256 hash
    hash_object = hashlib.sha256(input_string.encode())
    return hash_object.hexdigest()

def hash_image_content(image_content: bytes) -> str:
    """Generate a hash for the image content."""
    return hashlib.sha256(image_content).hexdigest()

