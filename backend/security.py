# backend/security.py

from passlib.context import CryptContext

# Configure passlib context
# We specify bcrypt as the default hashing algorithm
# We also mark sha256_crypt as deprecated for potential future migrations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hashes a plain password using the configured context."""
    return pwd_context.hash(password)