"""SQLAlchemy ORM models for the IEA application."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Persistent RSA keypair (hex "e:n" / "d:n"). Keys are per-user and reused
    # across logins so that messages can be sent to offline users and decrypted
    # after a later login. (See README for the security trade-off this implies.)
    rsa_public_key_hex = Column(String, nullable=True)
    rsa_private_key_hex = Column(String, nullable=True)


class ActiveSession(Base):
    __tablename__ = "active_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String, unique=True, index=True)
    rsa_public_key_hex = Column(String)  # "e:n" as hex string
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    encrypted_image = Column(LargeBinary, nullable=False)
    encrypted_des_key = Column(LargeBinary, nullable=False)
    signature = Column(LargeBinary, nullable=False)
    # Public key of the sender at send time, so the receiver can verify the
    # signature even after the sender logs out and rotates keys.
    sender_public_key_hex = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    delivered = Column(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)  # LOGIN, LOGOUT, MESSAGE_SENT, MESSAGE_RECEIVED, KEY_ROTATION
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    detail = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
