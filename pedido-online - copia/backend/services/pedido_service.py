from decimal import Decimal
from sqlalchemy import func
from backend.database import SessionLocal
from backend.models.order import Pedido, PedidoDetalle
from backend.models.inventory import Inventario, MovInventario
from backend.models.product import Producto
from backend.models.auditoria import Auditoria

def crear_pedido(id_usuario:int, productos:list[dict]):
    db = SessionLocal()
    try:
        total = Decimal("0.00")
        for pr in productos:
            total += Decimal(str(pr["precio_unitario"])) * int(pr["cantidad"])
        p = Pedido(id_usuario=id_usuario, estado="Pendiente", total_pedido=total)
        db.add(p)
        db.flush()
        for pr in productos:
            pid = int(pr["id_producto"])
            cant = int(pr["cantidad"])
            precio = Decimal(str(pr["precio_unitario"]))
            inv = db.query(Inventario).filter(Inventario.id_producto==pid).with_for_update().first()
            if not inv or inv.cantidad_actual < cant:
                db.rollback()
                return None, f"Sin stock suficiente para el producto ID {pid}"
            inv.cantidad_actual -= cant
            det = PedidoDetalle(id_pedido=p.id_pedido, id_producto=pid, cantidad=cant, precio_unitario=precio)
            db.add(det)
            db.add(MovInventario(id_producto=pid, tipo_mov="Salida", cantidad=cant, descripcion=f"Pedido #{p.id_pedido}"))
        db.add(Auditoria(id_usuario=id_usuario, accion="Creación de pedido", tabla_afectada="pedidos"))
        db.commit()
        return p.id_pedido, None
    except Exception:
        db.rollback()
        return None, "Error al crear pedido"
    finally:
        db.close()

def historial(id_usuario:int):
    db = SessionLocal()
    try:
        rows = (
            db.query(Pedido.id_pedido, Pedido.fecha_pedido, Pedido.estado, Pedido.total_pedido, func.group_concat((PedidoDetalle.cantidad).op("||")(" x ").op("||")(Producto.nombre)))
            .join(PedidoDetalle, PedidoDetalle.id_pedido==Pedido.id_pedido)
            .join(Producto, Producto.id_producto==PedidoDetalle.id_producto)
            .filter(Pedido.id_usuario==id_usuario)
            .group_by(Pedido.id_pedido)
            .order_by(Pedido.fecha_pedido.desc())
            .all()
        )
        out = []
        for r in rows:
            out.append({
                "id_pedido": r[0],
                "fecha_pedido": r[1],
                "estado": r[2],
                "total_pedido": float(r[3]),
                "productos": r[4] if r[4] is not None else ""
            })
        return out
    finally:
        db.close()

def seguimiento(id_usuario:int):
    db = SessionLocal()
    try:
        rows = (
            db.query(Pedido.id_pedido, Pedido.fecha_pedido, Pedido.estado)
            .filter(Pedido.id_usuario==id_usuario)
            .order_by(Pedido.fecha_pedido.desc())
            .all()
        )
        return [{"id_pedido": r[0], "fecha_pedido": r[1], "estado": r[2]} for r in rows]
    finally:
        db.close()
