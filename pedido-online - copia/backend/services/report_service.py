from typing import List, Dict, Optional
from datetime import datetime, date
from sqlalchemy import MetaData, Table, select, func
from backend.database import SessionLocal


def _t(db, name: str) -> Table:
    md = MetaData()
    return Table(name, md, autoload_with=db.bind)


def _tables(db):
    usuarios   = _t(db, "usuarios")
    pedidos    = _t(db, "pedidos")
    detalle    = _t(db, "pedido_detalle")
    productos  = _t(db, "productos")
    return usuarios, pedidos, detalle, productos


def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None


def _in_range(d: Optional[date], dfrom: Optional[date], dto: Optional[date]) -> bool:
    if d is None:
        return False
    if dfrom and dto:
        return dfrom <= d <= dto
    if dfrom:
        return d >= dfrom
    if dto:
        return d <= dto
    return True


def _normalize_fecha(fe):
    if fe is None:
        return None
    if isinstance(fe, datetime):
        return fe.date()
    if isinstance(fe, date):
        return fe
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(fe), fmt).date()
        except Exception:
            pass
    return None


def report_orders(date_from: Optional[str], date_to: Optional[str], client_q: Optional[str]) -> List[Dict]:
    """
    Trae todos los pedidos con agregados y filtra en Python por fechas y cliente.
    """
    db = SessionLocal()
    try:
        usuarios, pedidos, detalle, _ = _tables(db)

        stmt = (
            select(
                pedidos.c.id_pedido.label("id"),
                pedidos.c.fecha_pedido.label("fecha"),
                usuarios.c.nombre.label("cliente_nombre"),
                usuarios.c.email.label("cliente_email"),
                pedidos.c.estado.label("estado"),
                pedidos.c.total_pedido.label("total"),
                func.coalesce(func.sum(detalle.c.cantidad), 0).label("productos"),
            )
            .select_from(
                pedidos.join(usuarios, usuarios.c.id_usuario == pedidos.c.id_usuario)
                       .join(detalle, detalle.c.id_pedido == pedidos.c.id_pedido, isouter=True)
            )
            .group_by(
                pedidos.c.id_pedido,
                pedidos.c.fecha_pedido,
                usuarios.c.nombre,
                usuarios.c.email,
                pedidos.c.estado,
                pedidos.c.total_pedido,
            )
            .order_by(pedidos.c.id_pedido.desc())
        )

        rows = db.execute(stmt).mappings().all()

        dfrom = _parse_date(date_from)
        dto   = _parse_date(date_to)
        term  = (client_q or "").strip().lower()

        out: List[Dict] = []
        for r in rows:
            fdate = _normalize_fecha(r["fecha"])
            if not _in_range(fdate, dfrom, dto):
                continue
            if term:
                n = (r["cliente_nombre"] or "").lower()
                e = (r["cliente_email"]  or "").lower()
                if term not in n and term not in e:
                    continue
            out.append({
                "id": int(r["id"]),
                "fecha": r["fecha"],  
                "cliente_nombre": r["cliente_nombre"],
                "cliente_email": r["cliente_email"],
                "estado": r["estado"],
                "total": float(r["total"] or 0),
                "productos": int(r["productos"] or 0),
            })
        return out
    finally:
        db.close()


def report_orders_by_status(status: str, date_from: Optional[str], date_to: Optional[str]) -> List[Dict]:
    """
    Igual que report_orders, pero filtrando por estado además de fechas.
    """
    db = SessionLocal()
    try:
        usuarios, pedidos, detalle, _ = _tables(db)

        stmt = (
            select(
                pedidos.c.id_pedido.label("id"),
                pedidos.c.fecha_pedido.label("fecha"),
                usuarios.c.nombre.label("cliente_nombre"),
                usuarios.c.email.label("cliente_email"),
                pedidos.c.estado.label("estado"),
                pedidos.c.total_pedido.label("total"),
                func.coalesce(func.sum(detalle.c.cantidad), 0).label("productos"),
            )
            .select_from(
                pedidos.join(usuarios, usuarios.c.id_usuario == pedidos.c.id_usuario)
                       .join(detalle, detalle.c.id_pedido == pedidos.c.id_pedido, isouter=True)
            )
            .group_by(
                pedidos.c.id_pedido,
                pedidos.c.fecha_pedido,
                usuarios.c.nombre,
                usuarios.c.email,
                pedidos.c.estado,
                pedidos.c.total_pedido,
            )
            .order_by(pedidos.c.id_pedido.desc())
        )

        rows = db.execute(stmt).mappings().all()

        dfrom = _parse_date(date_from)
        dto   = _parse_date(date_to)
        st    = str(status or "").strip()

        out: List[Dict] = []
        for r in rows:
            if st and r["estado"] != st:
                continue
            fdate = _normalize_fecha(r["fecha"])
            if not _in_range(fdate, dfrom, dto):
                continue
            out.append({
                "id": int(r["id"]),
                "fecha": r["fecha"],
                "cliente_nombre": r["cliente_nombre"],
                "cliente_email": r["cliente_email"],
                "estado": r["estado"],
                "total": float(r["total"] or 0),
                "productos": int(r["productos"] or 0),
            })
        return out
    finally:
        db.close()


def report_products(kind: str) -> List[Dict]:
    """
    Productos más/menos solicitados (sin fechas).
    """
    db = SessionLocal()
    try:
        _, _, detalle, productos = _tables(db)

        agg = (
            select(
                detalle.c.id_producto,
                func.sum(detalle.c.cantidad).label("cant"),
                func.sum(detalle.c.cantidad * detalle.c.precio_unitario).label("importe"),
                func.count(detalle.c.id_pedido).label("lineas"),
            )
            .group_by(detalle.c.id_producto)
            .subquery()
        )

        stmt = (
            select(
                productos.c.id_producto,
                productos.c.nombre,
                agg.c.cant,
                agg.c.importe,
                agg.c.lineas,
            )
            .select_from(productos.join(agg, agg.c.id_producto == productos.c.id_producto, isouter=True))
        )

        if (kind or "top") == "low":
            stmt = stmt.order_by(func.coalesce(agg.c.cant, 0).asc(), productos.c.id_producto.asc())
        else:
            stmt = stmt.order_by(func.coalesce(agg.c.cant, 0).desc(), productos.c.id_producto.asc())

        rows = db.execute(stmt).mappings().all()
        return [{
            "id_producto": int(r["id_producto"]),
            "nombre": r["nombre"],
            "cantidad_solicitada": int(r["cant"] or 0),
            "importe_total": float(r["importe"] or 0),
            "lineas": int(r["lineas"] or 0),
        } for r in rows]
    finally:
        db.close()
