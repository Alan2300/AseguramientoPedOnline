from typing import List, Dict, Optional
from werkzeug.security import generate_password_hash
from sqlalchemy import MetaData, Table, select, insert, update, delete, and_, or_, func
from backend.database import SessionLocal

ROLE_NAMES = {1: "Administrador", 2: "Cliente"}

def _tusuarios(db):
    md = MetaData()
    return Table("usuarios", md, autoload_with=db.bind)

def _row_to_user_dict(r) -> Dict:
    if r is None:
        return {}
    d = {
        "id_usuario": int(r["id_usuario"]),
        "nombre": r.get("nombre"),
        "email": r.get("email"),
        "id_rol": int(r.get("id_rol", 0)) if r.get("id_rol") is not None else None,
    }
    if "password" in r:
        d["password"] = r["password"]
    if d.get("id_rol") is not None:
        d["rol_nombre"] = ROLE_NAMES.get(d["id_rol"], str(d["id_rol"]))
    return d

def find_user_by_email(email: str) -> Optional[Dict]:
    db = SessionLocal()
    try:
        t = _tusuarios(db)
        row = db.execute(
            select(t.c.id_usuario, t.c.nombre, t.c.email, t.c.password, t.c.id_rol)
            .where(t.c.email == email)
        ).mappings().first()
        return _row_to_user_dict(row) if row else None
    finally:
        db.close()

def create_user(nombre: str, email: str, password: str, id_rol: int) -> Optional[str]:
    db = SessionLocal()
    try:
        t = _tusuarios(db)
        exists = db.execute(select(t.c.id_usuario).where(t.c.email == email)).first()
        if exists:
            return "El correo ya está registrado"
        hashed = generate_password_hash(password) if password else generate_password_hash("123456")
        db.execute(insert(t).values(nombre=nombre, email=email, password=hashed, id_rol=id_rol))
        db.commit()
        return None
    finally:
        db.close()

def list_users(q: Optional[str] = None, role_id: Optional[int] = None) -> List[Dict]:
    db = SessionLocal()
    try:
        t = _tusuarios(db)
        stmt = select(t.c.id_usuario, t.c.nombre, t.c.email, t.c.id_rol)
        conds = []
        if q:
            ql = f"%{q.strip().lower()}%"
            conds.append(
                or_(
                    func.lower(t.c.nombre).like(ql),
                    func.lower(t.c.email).like(ql),
                )
            )
        if role_id:
            conds.append(t.c.id_rol == int(role_id))
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(t.c.id_usuario.desc())
        rows = db.execute(stmt).mappings().all()
        return [_row_to_user_dict(r) for r in rows]
    finally:
        db.close()

def update_user(user_id: int, nombre: str, email: str, password: Optional[str], id_rol: int) -> Optional[str]:
    db = SessionLocal()
    try:
        t = _tusuarios(db)
        dup = db.execute(
            select(t.c.id_usuario).where(and_(t.c.email == email, t.c.id_usuario != user_id))
        ).first()
        if dup:
            return "Ese correo ya pertenece a otro usuario"
        values = {"nombre": nombre, "email": email, "id_rol": id_rol}
        if password:
            values["password"] = generate_password_hash(password)
        res = db.execute(update(t).where(t.c.id_usuario == user_id).values(**values))
        if res.rowcount == 0:
            return "Usuario no encontrado"
        db.commit()
        return None
    finally:
        db.close()

def delete_user(user_id: int) -> Optional[str]:
    db = SessionLocal()
    try:
        t = _tusuarios(db)
        res = db.execute(delete(t).where(t.c.id_usuario == user_id))
        if res.rowcount == 0:
            return "Usuario no encontrado"
        db.commit()
        return None
    finally:
        db.close()
