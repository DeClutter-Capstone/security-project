"""Authentication helpers: bcrypt hashing, session tokens, and the
in-memory store of per-session RSA private keys.
"""

import secrets

import bcrypt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import ActiveSession, User

# Maps session_token -> RSA private key tuple (d, n).
# Private keys live ONLY here, in server memory. They are never written to the
# database and are discarded on logout / restart.
SESSION_KEYS = {}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_session_token() -> str:
    return secrets.token_urlsafe(32)


def get_session(token: str, db: Session) -> ActiveSession:
    return db.query(ActiveSession).filter(ActiveSession.session_token == token).first()


def _token_from_header(authorization: str) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return authorization.split(" ", 1)[1].strip()


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: resolve the logged-in user from the Bearer token."""
    token = _token_from_header(authorization)
    session = get_session(token, db)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    # Stash the token on the user object for convenience in route handlers.
    user._session_token = token
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency that additionally requires admin privileges."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
