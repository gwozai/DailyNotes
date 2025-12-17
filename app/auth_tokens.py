"""
Secure token generation and validation for password reset and magic links.

Security measures:
- Tokens are cryptographically random (32 bytes, URL-safe)
- Tokens are hashed with SHA-256 before storage
- Rate limiting prevents brute force and email spam
- Short expiration times limit exposure window
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
import logging

from app import db
from app.models import User, AuthToken, RateLimit

logger = logging.getLogger(__name__)

# Token expiration times
PASSWORD_RESET_EXPIRY = timedelta(hours=1)
MAGIC_LINK_EXPIRY = timedelta(minutes=15)

# Rate limiting: 3 requests per email per hour
RATE_LIMIT_WINDOW = timedelta(hours=1)
RATE_LIMIT_MAX_REQUESTS = 3


def generate_token() -> str:
    """
    Generate a cryptographically secure random token.

    Returns a 43-character URL-safe base64 string (32 bytes of entropy).
    """
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """
    Hash a token using SHA-256 for secure storage.

    The hash is stored in the database, not the raw token.
    This means even if the database is compromised, tokens cannot be recovered.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def hash_email_for_rate_limit(email: str) -> str:
    """
    Hash email for rate limiting.

    Uses SHA-256 to create a consistent identifier without storing PII.
    """
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()


def check_rate_limit(email: str, action_type: str) -> bool:
    """
    Check if action is rate limited for this email.

    Args:
        email: User's email address
        action_type: Type of action ('password_reset' or 'magic_link')

    Returns:
        True if request is allowed, False if rate limited
    """
    identifier = hash_email_for_rate_limit(email)
    cutoff = datetime.now(timezone.utc) - RATE_LIMIT_WINDOW

    # Count recent requests
    count = RateLimit.query.filter(
        RateLimit.identifier == identifier,
        RateLimit.action_type == action_type,
        RateLimit.timestamp > cutoff,
    ).count()

    return count < RATE_LIMIT_MAX_REQUESTS


def record_rate_limit(email: str, action_type: str):
    """
    Record a rate-limited action.

    Args:
        email: User's email address
        action_type: Type of action ('password_reset' or 'magic_link')
    """
    identifier = hash_email_for_rate_limit(email)
    rate_limit = RateLimit(identifier=identifier, action_type=action_type)
    db.session.add(rate_limit)
    db.session.commit()


def create_auth_token(user: User, token_type: str) -> str:
    """
    Create a new auth token for a user.

    Invalidates any existing unused tokens of the same type for security.

    Args:
        user: User to create token for
        token_type: Type of token ('password_reset' or 'magic_link')

    Returns:
        The raw token (for sending in email). This is the only time
        the raw token is available - it's not stored in the database.
    """
    # Invalidate any existing unused tokens of this type for this user
    AuthToken.query.filter(
        AuthToken.user_id == user.uuid,
        AuthToken.token_type == token_type,
        AuthToken.used_at.is_(None),
    ).delete()
    db.session.commit()

    # Generate new token
    raw_token = generate_token()
    token_hash = hash_token(raw_token)

    # Set expiry based on token type
    if token_type == "password_reset":
        expiry = datetime.now(timezone.utc) + PASSWORD_RESET_EXPIRY
    else:  # magic_link
        expiry = datetime.now(timezone.utc) + MAGIC_LINK_EXPIRY

    auth_token = AuthToken(
        user_id=user.uuid,
        token_hash=token_hash,
        token_type=token_type,
        expires_at=expiry,
    )
    db.session.add(auth_token)
    db.session.commit()

    logger.info(f"Created {token_type} token for user {user.username}")
    return raw_token


def validate_token(raw_token: str, token_type: str) -> Optional[User]:
    """
    Validate a token and return the associated user if valid.

    Uses hash comparison which provides constant-time behavior through
    the database query (preventing timing attacks).

    Args:
        raw_token: The raw token from the URL
        token_type: Expected token type ('password_reset' or 'magic_link')

    Returns:
        User if token is valid, None otherwise
    """
    token_hash = hash_token(raw_token)

    auth_token = AuthToken.query.filter(
        AuthToken.token_hash == token_hash,
        AuthToken.token_type == token_type,
        AuthToken.used_at.is_(None),
        AuthToken.expires_at > datetime.now(timezone.utc),
    ).first()

    if not auth_token:
        logger.warning(f"Invalid or expired {token_type} token attempted")
        return None

    return User.query.get(auth_token.user_id)


def invalidate_token(raw_token: str) -> bool:
    """
    Mark a token as used.

    Args:
        raw_token: The raw token to invalidate

    Returns:
        True if token was found and invalidated, False otherwise
    """
    token_hash = hash_token(raw_token)

    auth_token = AuthToken.query.filter(AuthToken.token_hash == token_hash).first()

    if auth_token:
        auth_token.used_at = datetime.now(timezone.utc)
        db.session.add(auth_token)
        db.session.commit()
        logger.info(f"Invalidated {auth_token.token_type} token")
        return True

    return False


def cleanup_expired_tokens():
    """
    Remove expired tokens and old rate limit records.

    Can be called periodically (e.g., daily) to keep the database clean.
    """
    cutoff = datetime.now(timezone.utc)

    # Delete expired tokens
    expired_count = AuthToken.query.filter(AuthToken.expires_at < cutoff).delete()

    # Delete old used tokens (keep for a day for audit)
    used_cutoff = cutoff - timedelta(days=1)
    used_count = AuthToken.query.filter(
        AuthToken.used_at.isnot(None), AuthToken.used_at < used_cutoff
    ).delete()

    # Clean up old rate limit records
    rate_cutoff = cutoff - RATE_LIMIT_WINDOW
    rate_count = RateLimit.query.filter(RateLimit.timestamp < rate_cutoff).delete()

    db.session.commit()

    logger.info(
        f"Cleanup: removed {expired_count} expired tokens, "
        f"{used_count} used tokens, {rate_count} rate limit records"
    )


def get_user_by_email(email: str) -> Optional[User]:
    """
    Find a user by their email address.

    Email lookup is case-insensitive.

    Args:
        email: Email address to search for

    Returns:
        User if found, None otherwise
    """
    if not email:
        return None

    email_normalized = email.lower().strip()

    # We need to check all users since email is encrypted
    # This is not ideal for large user bases, but acceptable for self-hosted
    users = User.query.all()
    for user in users:
        if user.email and user.email.lower() == email_normalized:
            return user

    return None
