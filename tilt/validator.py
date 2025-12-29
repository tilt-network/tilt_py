import base64
import binascii
import re


def is_valid_api_key(key: str) -> bool:
    """
    Validate an API key in the following format:
    - Starts exactly with 'sk_'
    - Followed by exactly 86 characters in base64url encoding (without padding)
    - Decodes to precisely 64 random bytes

    Returns True if valid, False otherwise.
    """
    if not key.startswith("sk_"):
        return False

    encoded = key[3:]
    if len(encoded) != 86:
        return False

    if not re.match(r"^[A-Za-z0-9\-_]+$", encoded):
        return False

    try:
        decoded = base64.urlsafe_b64decode(encoded + "==")
        return len(decoded) == 64
    except (binascii.Error, ValueError):
        return False
