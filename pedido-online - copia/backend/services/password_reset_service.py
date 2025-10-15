import os
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.user import Usuario
from backend.models.password_reset import PasswordReset
import hashlib


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def create_reset_token(email: str):
    """
    Si el usuario existe, crea un token de reseteo y devuelve:
      ( user_info_dict, raw_token )
    user_info_dict es un dict plano (no ORM) con: id_usuario, nombre, email
    """
    db: Session = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.email == (email or "").lower()).first()
        if not user:
            return None, None

        raw_token = secrets.token_urlsafe(48)
        token_hash = _sha256(raw_token)
        ttl = int(os.getenv("RESET_TOKEN_TTL_MINUTES", "30"))
        expires = datetime.utcnow() + timedelta(minutes=ttl)

        pr = PasswordReset(
            user_id=user.id_usuario,
            token_hash=token_hash,
            expires_at=expires,
            created_at=datetime.utcnow()
        )
        db.add(pr)
        db.commit()

        user_info = {
            "id_usuario": user.id_usuario,
            "nombre": user.nombre,
            "email": user.email
        }
        return user_info, raw_token
    except Exception:
        db.rollback()
        return None, None
    finally:
        db.close()


def consume_reset_token(raw_token: str):
    """
    Devuelve un dict con datos del token si es válido (no usado, no expirado):
      { "pr_id": int, "user_id": int }
    Si es inválido/expirado/usado -> None
    """
    db: Session = SessionLocal()
    try:
        token_hash = _sha256(raw_token)
        pr = db.query(PasswordReset).filter(PasswordReset.token_hash == token_hash).first()
        if not pr or pr.used_at is not None or pr.expires_at < datetime.utcnow():
            return None
        return {"pr_id": pr.id_reset, "user_id": pr.user_id}
    finally:
        db.close()


def mark_token_used(pr_id: int) -> bool:
    db: Session = SessionLocal()
    try:
        pr = db.query(PasswordReset).filter(PasswordReset.id_reset == pr_id).first()
        if not pr:
            return False
        pr.used_at = datetime.utcnow()
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()
