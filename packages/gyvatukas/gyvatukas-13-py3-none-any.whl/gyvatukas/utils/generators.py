import secrets


def get_random_secure_string(length: int) -> str:
    """Get random secure string generated by `secrets` module."""
    return secrets.token_urlsafe(length)
