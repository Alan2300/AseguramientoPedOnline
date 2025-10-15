from decimal import Decimal
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.product import Producto
from backend.models.inventory import Inventario

def _to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def list_products():
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(
                Producto.id_producto,
                Producto.nombre,
                Producto.descripcion,
                Producto.precio_unitario,
                Producto.imagen,
                Inventario.cantidad_actual
            )
            .outerjoin(Inventario, Inventario.id_producto == Producto.id_producto)
            .order_by(Producto.id_producto.asc())
            .all()
        )
        out = []
        for r in rows:
            out.append({
                "id_producto": int(r.id_producto),
                "nombre": r.nombre,
                "descripcion": r.descripcion or "",
                "precio_unitario": _to_float(r.precio_unitario),
                "imagen": r.imagen or "",
                "stock": int(r.cantidad_actual or 0),
            })
        return out
    finally:
        db.close()

def get_product(product_id: int):
    db: Session = SessionLocal()
    try:
        p = (
            db.query(
                Producto.id_producto,
                Producto.nombre,
                Producto.descripcion,
                Producto.precio_unitario,
                Producto.imagen,
                Inventario.cantidad_actual
            )
            .outerjoin(Inventario, Inventario.id_producto == Producto.id_producto)
            .filter(Producto.id_producto == product_id)
            .first()
        )
        if not p:
            return None
        return {
            "id_producto": int(p.id_producto),
            "nombre": p.nombre,
            "descripcion": p.descripcion or "",
            "precio_unitario": _to_float(p.precio_unitario),
            "imagen": p.imagen or "",
            "stock": int(p.cantidad_actual or 0),
        }
    finally:
        db.close()

def create_product(data: dict):
    db: Session = SessionLocal()
    try:
        p = Producto(
            nombre=(data.get("nombre") or "").strip(),
            descripcion=(data.get("descripcion") or "").strip(),
            precio_unitario=Decimal(str(data.get("precio_unitario") or data.get("precio") or 0)),
            imagen=(data.get("imagen") or "").strip(),
        )
        db.add(p)
        db.flush()
        if data.get("stock") is not None:
            inv = db.query(Inventario).filter(Inventario.id_producto == p.id_producto).first()
            if not inv:
                inv = Inventario(id_producto=p.id_producto, cantidad_actual=int(data.get("stock") or 0))
                db.add(inv)
            else:
                inv.cantidad_actual = int(data.get("stock") or 0)
        db.commit()
        return get_product(p.id_producto)
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()

def update_product(product_id: int, data: dict):
    db: Session = SessionLocal()
    try:
        p = db.query(Producto).filter(Producto.id_producto == product_id).first()
        if not p:
            return None
        if "nombre" in data:
            p.nombre = (data.get("nombre") or "").strip()
        if "descripcion" in data:
            p.descripcion = (data.get("descripcion") or "").strip()
        if "precio_unitario" in data or "precio" in data:
            p.precio_unitario = Decimal(str(data.get("precio_unitario") or data.get("precio") or 0))
        if "imagen" in data:
            p.imagen = (data.get("imagen") or "").strip()
        if "stock" in data:
            inv = db.query(Inventario).filter(Inventario.id_producto == p.id_producto).first()
            if not inv:
                inv = Inventario(id_producto=p.id_producto, cantidad_actual=int(data.get("stock") or 0))
                db.add(inv)
            else:
                inv.cantidad_actual = int(data.get("stock") or 0)
        db.commit()
        return get_product(product_id)
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()

def delete_product(product_id: int):
    db: Session = SessionLocal()
    try:
        inv = db.query(Inventario).filter(Inventario.id_producto == product_id).first()
        if inv:
            db.delete(inv)
        p = db.query(Producto).filter(Producto.id_producto == product_id).first()
        if not p:
            db.rollback()
            return False
        db.delete(p)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()
