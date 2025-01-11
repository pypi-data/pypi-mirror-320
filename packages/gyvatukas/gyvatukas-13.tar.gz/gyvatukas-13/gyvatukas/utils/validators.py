import logging

import emval

_logger = logging.getLogger("gyvatukas")


def is_email_valid(email: str, perform_dns_check: bool = False) -> tuple[bool, str]:
    """Check if email is valid. If check_deliverability is True, will also check if email is deliverable.
    If email is valid, returns normalized email, otherwise returns the original email.

    ❗ Does not do dns check since `emval` does not support it yet.

    Uses https://github.com/bnkc/emval lib.
    """
    _logger.debug("validating email `%s", email)

    try:
        validated = emval.validate_email(
            email,
        )
    except Exception as e:
        _logger.exception(f"email `{email}` validation failed with {e}")
        return False, email

    return True, validated.normalized
