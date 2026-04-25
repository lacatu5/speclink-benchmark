import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from ..config import SECRET_KEY, TOKEN_EXPIRY_HOURS
from ..database import get_connection
from ..models.user import User


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    hashed = hashlib.scrypt(
        password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32
    )
    return f"{salt.hex()}:{hashed.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt_hex, stored_hash = password_hash.split(":")
    hashed = hashlib.scrypt(
        password.encode(), salt=bytes.fromhex(salt_hex), n=16384, r=8, p=1, dklen=32
    )
    return hmac.compare_digest(hashed.hex(), stored_hash)


def generate_token(user_id: int) -> str:
    payload = f"{user_id}:{datetime.utcnow().isoformat()}"
    signature = hmac.new(
        SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"


def create_user(username: str, email: str, password: str) -> User:
    conn = get_connection()
    password_hash = hash_password(password)
    cursor = conn.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash),
    )
    conn.commit()
    user = get_user_by_id(cursor.lastrowid)
    conn.close()
    return user


def get_user_by_id(user_id: int) -> User | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return User.from_row(row) if row else None


def authenticate(username: str, password: str) -> str | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    user = User.from_row(row)
    if not verify_password(password, user.password_hash):
        return None
    return generate_token(user.id)
