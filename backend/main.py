"""
IEA - Image Encryption Application
FastAPI backend wiring together from-scratch DES + RSA.

Security model:
  * On login the server generates a fresh RSA keypair.
  * The PUBLIC key is stored in active_sessions (as hex) in the DB.
  * The PRIVATE key is kept only in the in-memory SESSION_KEYS dict.
  * Keys are discarded on logout.
  * Images are encrypted with a random per-message DES key.
  * The DES key is RSA-encrypted to the receiver and RSA-signed by the sender.
  * The server never stores the raw image or the raw DES key.
"""

import os
import sys

# Make the backend directory importable whether launched as
# `uvicorn backend.main:app` (from repo root) or `uvicorn main:app` (from backend/).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import base64
import secrets
from datetime import datetime

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

import des
import rsa
from auth import (
    SESSION_KEYS,
    create_session_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from database import Base, SessionLocal, engine, get_db
from models import ActiveSession, AuditLog, Message, User
from ws_manager import ConnectionManager

app = FastAPI(title="IEA - Image Encryption Application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()

FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend"
)


# --------------------------------------------------------------------------- #
# Request models
# --------------------------------------------------------------------------- #
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class DecryptRequest(BaseModel):
    message_id: int


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def log_audit(db: Session, event_type: str, user_id, detail: str):
    db.add(AuditLog(event_type=event_type, user_id=user_id, detail=detail))
    db.commit()


def is_online(db: Session, user_id: int) -> bool:
    return (
        db.query(ActiveSession).filter(ActiveSession.user_id == user_id).first()
        is not None
    )


def latest_session(db: Session, user_id: int) -> ActiveSession:
    return (
        db.query(ActiveSession)
        .filter(ActiveSession.user_id == user_id)
        .order_by(ActiveSession.created_at.desc())
        .first()
    )


def ensure_keypair(db: Session, user: User):
    """Return (public_key, private_key) for a user, generating and persisting a
    keypair the first time. Keys persist so offline users can still receive."""
    if not user.rsa_public_key_hex or not user.rsa_private_key_hex:
        public_key, private_key = rsa.generate_keypair()
        user.rsa_public_key_hex = rsa.key_to_hex(public_key)
        user.rsa_private_key_hex = rsa.key_to_hex(private_key)
        db.commit()
        log_audit(db, "KEY_ROTATION", user.id, f"RSA keypair generated for {user.username}")
    return rsa.hex_to_key(user.rsa_public_key_hex), rsa.hex_to_key(user.rsa_private_key_hex)


# --------------------------------------------------------------------------- #
# Startup: create tables + seed data
# --------------------------------------------------------------------------- #
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            seed = [
                ("admin", "admin123", True),
                ("alice", "alice123", False),
                ("bob", "bob123", False),
            ]
            for username, password, is_admin in seed:
                pub, priv = rsa.generate_keypair()
                db.add(
                    User(
                        username=username,
                        password_hash=hash_password(password),
                        is_admin=is_admin,
                        rsa_public_key_hex=rsa.key_to_hex(pub),
                        rsa_private_key_hex=rsa.key_to_hex(priv),
                    )
                )
            db.commit()
            print("Seeded default users: admin/admin123, alice/alice123, bob/bob123")
    finally:
        db.close()


# --------------------------------------------------------------------------- #
# Auth routes
# --------------------------------------------------------------------------- #
@app.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="Username and password required")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    # Generate the persistent keypair up front (offloaded; keygen blocks).
    public_key, private_key = await asyncio.to_thread(rsa.generate_keypair)
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        rsa_public_key_hex=rsa.key_to_hex(public_key),
        rsa_private_key_hex=rsa.key_to_hex(private_key),
    )
    db.add(user)
    db.commit()
    return {"success": True, "username": req.username}


@app.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Persistent per-user keypair (generated lazily if missing). Generation
    # blocks, so offload just the keygen to a worker thread; DB writes stay here.
    if not (user.rsa_public_key_hex and user.rsa_private_key_hex):
        public_key, private_key = await asyncio.to_thread(rsa.generate_keypair)
        user.rsa_public_key_hex = rsa.key_to_hex(public_key)
        user.rsa_private_key_hex = rsa.key_to_hex(private_key)
        db.commit()
        log_audit(db, "KEY_ROTATION", user.id, f"RSA keypair generated for {user.username}")
    else:
        public_key = rsa.hex_to_key(user.rsa_public_key_hex)
        private_key = rsa.hex_to_key(user.rsa_private_key_hex)
    token = create_session_token()

    db.add(
        ActiveSession(
            user_id=user.id,
            session_token=token,
            rsa_public_key_hex=rsa.key_to_hex(public_key),
        )
    )
    db.commit()

    # Keep the live private key in memory for this session as well.
    SESSION_KEYS[token] = private_key

    log_audit(db, "LOGIN", user.id, f"{user.username} logged in")

    return {"session_token": token, "username": user.username, "is_admin": user.is_admin}


@app.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    token = user._session_token
    db.query(ActiveSession).filter(ActiveSession.session_token == token).delete()
    db.commit()
    SESSION_KEYS.pop(token, None)
    log_audit(db, "LOGOUT", user.id, f"{user.username} logged out")
    return {"success": True}


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
@app.get("/users")
def list_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    others = db.query(User).filter(User.id != user.id).all()
    return [
        {"username": u.username, "online": is_online(db, u.id), "is_admin": u.is_admin}
        for u in others
    ]


# --------------------------------------------------------------------------- #
# Sending an image
# --------------------------------------------------------------------------- #
@app.post("/send-image")
async def send_image(
    receiver_username: str = Form(...),
    image: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receiver = db.query(User).filter(User.username == receiver_username).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    if receiver.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot send to yourself")

    # Persistent keys are always available, so sending NEVER depends on the
    # receiver being online. Keys are generated lazily if somehow missing.
    receiver_public_key, _ = ensure_keypair(db, receiver)
    sender_public_key, sender_private_key = ensure_keypair(db, user)

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image")

    # Step 1: random 8-byte DES key.
    des_key = secrets.token_bytes(8)

    # Step 2: encrypt the image with DES (key as latin-1 string).
    # Offloaded to a worker thread so the event loop never freezes.
    encrypted_image = await asyncio.to_thread(
        des.encrypt_bytes, image_bytes, des_key.decode("latin-1")
    )

    # Step 3: encrypt the DES key with the receiver's RSA public key.
    encrypted_des_key = rsa.rsa_encrypt(des_key, receiver_public_key)

    # Step 4: sign the DES key with the sender's RSA private key.
    signature = rsa.rsa_sign(des_key, sender_private_key)

    # Step 5: ALWAYS store the message, online or offline. Raw image/key never
    # persisted. An offline receiver gets it next time they fetch the thread.
    msg = Message(
        sender_id=user.id,
        receiver_id=receiver.id,
        encrypted_image=encrypted_image,
        encrypted_des_key=encrypted_des_key,
        signature=signature,
        sender_public_key_hex=rsa.key_to_hex(sender_public_key),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    log_audit(db, "MESSAGE_SENT", user.id, f"{user.username} -> {receiver.username} (msg {msg.id})")

    # Step 6: best-effort WebSocket notification. If the receiver has any live
    # connection, push to it; otherwise do nothing (message waits in the DB).
    for s in db.query(ActiveSession).filter(ActiveSession.user_id == receiver.id).all():
        if s.session_token in manager.active_connections:
            await manager.send_to_user(
                s.session_token, {"type": "new_message", "from": user.username}
            )

    return {"success": True, "message_id": msg.id}


# --------------------------------------------------------------------------- #
# Reading message metadata for a conversation
# --------------------------------------------------------------------------- #
@app.get("/messages/{other_username}")
def get_messages(
    other_username: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    other = db.query(User).filter(User.username == other_username).first()
    if not other:
        raise HTTPException(status_code=404, detail="User not found")

    msgs = (
        db.query(Message)
        .filter(
            ((Message.sender_id == user.id) & (Message.receiver_id == other.id))
            | ((Message.sender_id == other.id) & (Message.receiver_id == user.id))
        )
        .order_by(Message.timestamp.asc())
        .all()
    )

    result = []
    for m in msgs:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        result.append(
            {
                "id": m.id,
                "sender_username": sender.username if sender else "?",
                "is_mine": m.sender_id == user.id,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                "delivered": m.delivered,
                "encrypted_image": base64.b64encode(m.encrypted_image).decode(),
                "encrypted_des_key": base64.b64encode(m.encrypted_des_key).decode(),
                "signature": base64.b64encode(m.signature).decode(),
                "sender_public_key_hex": m.sender_public_key_hex,
            }
        )
    return result


# --------------------------------------------------------------------------- #
# Decrypting a message (receiver only)
# --------------------------------------------------------------------------- #
@app.post("/decrypt-message")
async def decrypt_message(
    req: DecryptRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msg = db.query(Message).filter(Message.id == req.message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.receiver_id != user.id:
        raise HTTPException(status_code=403, detail="You are not the recipient")

    # Use the receiver's persistent private key (works even for messages that
    # arrived while they were offline / before this login).
    _, private_key = ensure_keypair(db, user)

    # Step 1: recover the DES key with the receiver's private key.
    # Left-pad to 8 bytes in case leading zero bytes were stripped.
    des_key = rsa.rsa_decrypt(msg.encrypted_des_key, private_key).rjust(8, b"\x00")

    # Step 2: verify the DES key was signed by the sender (unmodified).
    sender_public_key = rsa.hex_to_key(msg.sender_public_key_hex)
    signature_valid = rsa.rsa_verify(des_key, msg.signature, sender_public_key)

    # Step 3: decrypt the image (offloaded to a worker thread).
    image_bytes = await asyncio.to_thread(
        des.decrypt_bytes, msg.encrypted_image, des_key.decode("latin-1")
    )

    # Mark delivered and audit.
    if not msg.delivered:
        msg.delivered = True
        db.commit()
    log_audit(db, "MESSAGE_RECEIVED", user.id, f"{user.username} decrypted msg {msg.id}")

    return {
        "image_base64": base64.b64encode(image_bytes).decode(),
        "signature_valid": bool(signature_valid),
    }


# --------------------------------------------------------------------------- #
# WebSocket
# --------------------------------------------------------------------------- #
@app.websocket("/ws/{session_token}")
async def websocket_endpoint(websocket: WebSocket, session_token: str):
    db = SessionLocal()
    try:
        session = (
            db.query(ActiveSession)
            .filter(ActiveSession.session_token == session_token)
            .first()
        )
    finally:
        db.close()

    if not session:
        await websocket.close(code=1008)
        return

    await manager.connect(session_token, websocket)
    try:
        while True:
            # Keep the connection open; we don't expect inbound messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_token)
    except Exception:
        manager.disconnect(session_token)


# --------------------------------------------------------------------------- #
# Admin routes (metadata only, never decrypts)
# --------------------------------------------------------------------------- #
@app.get("/admin/users")
def admin_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "online": is_online(db, u.id),
        }
        for u in users
    ]


@app.get("/admin/messages")
def admin_messages(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    msgs = db.query(Message).order_by(Message.timestamp.desc()).all()
    out = []
    for m in msgs:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        receiver = db.query(User).filter(User.id == m.receiver_id).first()
        out.append(
            {
                "id": m.id,
                "sender": sender.username if sender else "?",
                "receiver": receiver.username if receiver else "?",
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                "delivered": m.delivered,
            }
        )
    return out


@app.get("/admin/audit-log")
def admin_audit_log(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    result = []
    for log in logs:
        u = db.query(User).filter(User.id == log.user_id).first() if log.user_id else None
        result.append(
            {
                "id": log.id,
                "event_type": log.event_type,
                "username": u.username if u else None,
                "detail": log.detail,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
        )
    return result


@app.get("/admin/active-sessions")
def admin_active_sessions(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    sessions = db.query(ActiveSession).order_by(ActiveSession.created_at.desc()).all()
    out = []
    for s in sessions:
        u = db.query(User).filter(User.id == s.user_id).first()
        out.append(
            {
                "username": u.username if u else "?",
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
        )
    return out


# --------------------------------------------------------------------------- #
# Serve the frontend (mounted last so API routes take precedence)
# --------------------------------------------------------------------------- #
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
