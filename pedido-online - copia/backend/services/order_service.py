from datetime import datetime
from decimal import Decimal
import traceback
import logging
import os

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError

from backend.database import SessionLocal
from backend.models.order import Pedido, PedidoDetalle
from backend.models.product import Producto
from backend.models.inventory import Inventario
from backend.models.inventory_move import MovInventario
from backend.models.user import Usuario
from backend.services.email_service import send_email

log = logging.getLogger("orders")

ALLOWED_STATUSES = {"Pendiente", "En proceso", "Completado", "Cancelado"}

def _norm_items(items):
    out = []
    for it in items or []:
        pid = it.get("id_producto") or it.get("id") or it.get("producto_id") or it.get("productId") or it.get("idProd")
        qty = it.get("cantidad") or it.get("qty") or it.get("cant")
        try:
            pid = int(pid); qty = int(qty)
        except Exception:
            continue
        if pid > 0 and qty > 0:
            out.append({"id_producto": pid, "cantidad": qty})
    return out

def _render_admin_order_email(user, pedido_id, items_rows, total, front_url):
    filas = "".join(
        f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee">{r['nombre']}</td>
          <td style="padding:8px;text-align:right;border-bottom:1px solid #eee">{r['cantidad']}</td>
          <td style="padding:8px;text-align:right;border-bottom:1px solid #eee">Q {r['precio_unitario']:.2f}</td>
          <td style="padding:8px;text-align:right;border-bottom:1px solid #eee">Q {r['subtotal']:.2f}</td>
        </tr>
        """ for r in items_rows
    )
    admin_link = f"{front_url}/frontend/admin_pedidos.html"
    return f"""
<!doctype html><html lang="es"><meta charset="utf-8"><body style="font-family:Arial,Helvetica,sans-serif;background:#f6f7fb;padding:24px;color:#111">
<div style="max-width:640px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.08)">
  <div style="background:#0d6efd;color:#fff;padding:18px 22px;font-weight:700">Nuevo pedido #{pedido_id}</div>
  <div style="padding:22px">
    <p style="margin:0 0 12px">Cliente: <b>{getattr(user,'nombre',getattr(user,'name',''))}</b> &lt;{getattr(user,'email',getattr(user,'correo',''))}&gt;</p>
    <table style="width:100%;border-collapse:collapse;margin:8px 0 16px 0">
      <thead><tr style="background:#f3f4f6"><th style="text-align:left;padding:8px">Producto</th><th style="text-align:right;padding:8px">Cant.</th><th style="text-align:right;padding:8px">Precio</th><th style="text-align:right;padding:8px">Subtotal</th></tr></thead>
      <tbody>{filas}</tbody>
      <tfoot><tr><td colspan="3" style="padding:10px 8px;text-align:right;font-weight:700">Total</td><td style="padding:10px 8px;text-align:right;font-weight:700">Q {total:.2f}</td></tr></tfoot>
    </table>
    <a href="{admin_link}" style="display:inline-block;background:#0d6efd;color:#fff;text-decoration:none;padding:12px 18px;border-radius:10px;font-weight:700">Ver pedidos</a>
  </div>
  <div style="padding:14px 22px;background:#f9fafb;color:#6b7280;font-size:12px">Notificación automática • {os.getenv("APP_NAME","Pedidos App")}</div>
</div></body></html>
"""

def _render_customer_order_email(nombre, pedido_id, items_rows, total, front_url):
    filas = "".join(
        f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee">{r['nombre']}</td>
          <td style="padding:8px;text-align:right;border-bottom:1px solid #eee">{r['cantidad']}</td>
          <td style="padding:8px;text-align:right;border-bottom:1px solid #eee">Q {r['precio_unitario']:.2f}</td>
          <td style="padding:8px;text-align:right;border-bottom:1px solid #eee">Q {r['subtotal']:.2f}</td>
        </tr>
        """ for r in items_rows
    )
    track = f"{front_url}/frontend/seguimiento_pedidos.html?pedido={pedido_id}"
    return f"""
<!doctype html><html lang="es"><meta charset="utf-8"><body style="font-family:Arial,Helvetica,sans-serif;background:#f6f7fb;padding:24px;color:#111">
<div style="max-width:640px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.08)">
  <div style="background:#16a34a;color:#fff;padding:18px 22px;font-weight:700">¡Pedido recibido!</div>
  <div style="padding:22px">
    <p style="margin:0 0 12px">Hola {nombre or "cliente"},</p>
    <p style="margin:0 0 16px">Tu pedido <b>#{pedido_id}</b> fue creado correctamente. A continuación el resumen:</p>
    <table style="width:100%;border-collapse:collapse;margin:8px 0 16px 0">
      <thead><tr style="background:#f3f4f6"><th style="text-align:left;padding:8px">Producto</th><th style="text-align:right;padding:8px">Cant.</th><th style="text-align:right;padding:8px">Precio</th><th style="text-align:right;padding:8px">Subtotal</th></tr></thead>
      <tbody>{filas}</tbody>
      <tfoot><tr><td colspan="3" style="padding:10px 8px;text-align:right;font-weight:700">Total</td><td style="padding:10px 8px;text-align:right;font-weight:700">Q {total:.2f}</td></tr></tfoot>
    </table>
    <p>Podrás ver el estado del pedido en el siguiente enlace (deberás iniciar sesión):</p>
    <a href="{track}" style="display:inline-block;background:#0d6efd;color:#fff;text-decoration:none;padding:12px 18px;border-radius:10px;font-weight:700">Ver seguimiento</a>
  </div>
  <div style="padding:14px 22px;background:#f9fafb;color:#6b7280;font-size:12px">Gracias por tu compra • {os.getenv("APP_NAME","Pedidos App")}</div>
</div></body></html>
"""

def create_order(user_id: int, items: list):
    items = _norm_items(items)
    if not isinstance(user_id, int) or user_id <= 0:
        return None, "Usuario inválido"
    if not items:
        return None, "Carrito vacío o formato inválido"

    db: Session = SessionLocal()
    try:
        ids = [i["id_producto"] for i in items]
        prods = db.query(Producto).filter(Producto.id_producto.in_(ids)).all()
        prod_map = {p.id_producto: p for p in prods}
        faltantes = [pid for pid in set(ids) if pid not in prod_map]
        if faltantes:
            return None, f"Producto {faltantes[0]} no existe"

        invs = db.query(Inventario).filter(Inventario.id_producto.in_(ids)).all()
        inv_map = {i.id_producto: i for i in invs}

        total = Decimal("0.00")
        now = datetime.utcnow()

        pedido = Pedido(
            id_usuario=user_id,
            fecha_pedido=now,
            estado="Pendiente",
            total_pedido=Decimal("0.00"),
            fecha_actualizacion=now,
        )
        db.add(pedido)
        db.flush()

        email_rows = []
        for it in items:
            p = prod_map[it["id_producto"]]
            inv = inv_map.get(it["id_producto"])
            qty = int(it["cantidad"])
            precio = Decimal(str(p.precio_unitario or 0))

            if inv is not None and inv.cantidad_actual < qty:
                db.rollback()
                return None, f"Sin stock suficiente para {p.nombre}"

            subtotal = precio * qty
            total += subtotal

            det = PedidoDetalle(
                id_pedido=pedido.id_pedido,
                id_producto=p.id_producto,
                cantidad=qty,
                precio_unitario=precio
            )
            db.add(det)

            if inv is not None:
                inv.cantidad_actual = inv.cantidad_actual - qty
                mov = MovInventario(
                    id_producto=p.id_producto,
                    tipo_mov="Salida",
                    cantidad=qty,
                    fecha_mov=now,
                    descripcion=f"Pedido #{pedido.id_pedido}"
                )
                db.add(mov)

            email_rows.append({
                "nombre": p.nombre,
                "cantidad": qty,
                "precio_unitario": float(precio),
                "subtotal": float(subtotal)
            })

        pedido.total_pedido = total
        pedido.fecha_actualizacion = datetime.utcnow()
        db.commit()
        db.refresh(pedido)

        try:
            user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
            front = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:5500")

            try:
                html_admin = _render_admin_order_email(user, pedido.id_pedido, email_rows, float(total), front)
                to_list = []
                cfg = os.getenv("ORDER_NOTIFY_TO","").strip()
                if cfg:
                    to_list = [x.strip() for x in cfg.split(",") if x.strip()]
                elif os.getenv("ADMIN_EMAIL"):
                    to_list = [os.getenv("ADMIN_EMAIL")]
                else:
                    fallback = os.getenv("FROM_ADDR") or os.getenv("SMTP_USER")
                    if fallback:
                        to_list = [fallback]
                for addr in to_list:
                    try:
                        send_email(addr, f"Nuevo pedido #{pedido.id_pedido}", html_admin)
                    except Exception as se:
                        log.warning("No se pudo enviar notificación admin a %s: %s", addr, se)
            except Exception as e:
                log.warning("Fallo componiendo/enviando notificación admin: %s", e)

            # Cliente
            try:
                nombre_cli = (getattr(user, "nombre", None) or getattr(user, "name", None) or "").strip()
                email_cli = (getattr(user, "email", None) or getattr(user, "correo", None) or "").strip()
                if email_cli:
                    log.info("[EMAIL][CLIENT] Enviando confirmación a %s para pedido #%s", email_cli, pedido.id_pedido)
                    html_cli = _render_customer_order_email(nombre_cli, pedido.id_pedido, email_rows, float(total), front)
                    send_email(email_cli, f"Tu pedido #{pedido.id_pedido} fue creado", html_cli)
                else:
                    log.warning("[EMAIL][CLIENT] Usuario %s sin email/correo; no se envía confirmación.", user_id)
            except Exception as e:
                log.warning("[EMAIL][CLIENT] Error al enviar confirmación: %s", e)

        except Exception as e:
            log.warning("Bloque notificaciones falló: %s", e)

        return {
            "id_pedido": int(pedido.id_pedido),
            "total_pedido": float(pedido.total_pedido or 0),
            "estado": pedido.estado,
            "fecha_pedido": pedido.fecha_pedido.isoformat()
        }, None

    except (IntegrityError, DataError) as e:
        db.rollback()
        log.error("[PEDIDOS][DB] %s", str(e)); log.debug(traceback.format_exc())
        return None, "Datos inválidos al guardar el pedido"
    except SQLAlchemyError as e:
        db.rollback()
        log.error("[PEDIDOS][SQLA] %s", str(e)); log.debug(traceback.format_exc())
        return None, "Error al crear pedido en la base de datos"
    except Exception as e:
        db.rollback()
        log.error("[PEDIDOS][EXC] %s", str(e)); log.debug(traceback.format_exc())
        return None, "Error al crear pedido"
    finally:
        db.close()

def list_orders():
    db = SessionLocal()
    try:
        q = (
            db.query(
                Pedido.id_pedido.label("id"),
                Pedido.fecha_pedido.label("fecha"),
                Pedido.estado.label("estado"),
                Usuario.nombre.label("cliente_nombre"),
                Usuario.email.label("cliente_email"),
                func.sum(PedidoDetalle.cantidad).label("productos"),
                func.sum(PedidoDetalle.cantidad * PedidoDetalle.precio_unitario).label("total"),
            )
            .join(Usuario, Usuario.id_usuario == Pedido.id_usuario)
            .join(PedidoDetalle, PedidoDetalle.id_pedido == Pedido.id_pedido)
            .group_by(
                Pedido.id_pedido,
                Pedido.fecha_pedido,
                Pedido.estado,
                Usuario.nombre,
                Usuario.email,
            )
            .order_by(Pedido.id_pedido.desc())
        )
        rows = q.all()
        if not rows:
            return []

        order_ids = [int(r.id) for r in rows]
        prod_rows = (
            db.query(PedidoDetalle.id_pedido, Producto.nombre)
            .join(Producto, Producto.id_producto == PedidoDetalle.id_producto)
            .filter(PedidoDetalle.id_pedido.in_(order_ids))
            .all()
        )
        names_map = {}
        for oid, pname in prod_rows:
            names_map.setdefault(int(oid), set()).add(pname or "")

        out = []
        for r in rows:
            fecha = r.fecha.strftime("%Y-%m-%d")
            out.append({
                "id": int(r.id),
                "fecha": fecha,
                "estado": r.estado,
                "cliente_nombre": r.cliente_nombre,
                "cliente_email": r.cliente_email,
                "productos": int(r.productos or 0),
                "total": float(r.total or 0),
                "product_names": ", ".join(sorted(names_map.get(int(r.id), []))),
            })
        return out
    finally:
        db.close()


def update_order_status(order_id: int, new_status: str):
    if new_status not in ALLOWED_STATUSES:
        return None, "Estado inválido"
    db = SessionLocal()
    try:
        pedido = db.query(Pedido).filter(Pedido.id_pedido == order_id).first()
        if not pedido:
            return None, "Pedido no encontrado"
        old = pedido.estado
        pedido.estado = new_status
        pedido.fecha_actualizacion = datetime.utcnow()
        db.commit()
        db.refresh(pedido)

        user = db.query(Usuario).filter(Usuario.id_usuario == pedido.id_usuario).first()
        data = {
            "id": pedido.id_pedido,
            "estado_anterior": old,
            "estado_nuevo": pedido.estado,
            "cliente_nombre": getattr(user, "nombre", "") if user else "",
            "cliente_email": getattr(user, "email", getattr(user, "correo", "")) if user else "",
        }
        return data, None
    finally:
        db.close()



def list_orders_by_user(user_id: int):
    db = SessionLocal()
    try:
        q = (
            db.query(
                Pedido.id_pedido.label("id"),
                Pedido.fecha_pedido.label("fecha"),
                Pedido.estado.label("estado"),
                func.sum(PedidoDetalle.cantidad).label("productos"),
                func.sum(PedidoDetalle.cantidad * PedidoDetalle.precio_unitario).label("total"),
            )
            .join(PedidoDetalle, PedidoDetalle.id_pedido == Pedido.id_pedido)
            .filter(Pedido.id_usuario == user_id)
            .group_by(Pedido.id_pedido, Pedido.fecha_pedido, Pedido.estado)
            .order_by(Pedido.id_pedido.desc())
        )
        rows = q.all()
        if not rows:
            return []

        order_ids = [int(r.id) for r in rows]
        prod_rows = (
            db.query(PedidoDetalle.id_pedido, Producto.nombre)
            .join(Producto, Producto.id_producto == PedidoDetalle.id_producto)
            .filter(PedidoDetalle.id_pedido.in_(order_ids))
            .all()
        )
        names_map = {}
        for oid, pname in prod_rows:
            names_map.setdefault(int(oid), set()).add(pname or "")

        out = []
        for r in rows:
            fecha = r.fecha.strftime("%Y-%m-%d")
            out.append({
                "id": int(r.id),
                "fecha": fecha,
                "estado": r.estado,
                "productos": int(r.productos or 0),
                "total": float(r.total or 0),
                "product_names": ", ".join(sorted(names_map.get(int(r.id), []))),
            })
        return out
    finally:
        db.close()

