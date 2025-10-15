from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base

class Pedido(Base):
    __tablename__ = "pedidos"
    id_pedido = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, nullable=False)
    fecha_pedido = Column(DateTime, nullable=False, default=datetime.utcnow)
    estado = Column(String(50), nullable=False, default="Pendiente")
    total_pedido = Column(Numeric(10, 2), nullable=False, default=0)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow)

class PedidoDetalle(Base):
    __tablename__ = "pedido_detalle" 
    id_item = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Numeric(10, 2), nullable=False, default=0)  
