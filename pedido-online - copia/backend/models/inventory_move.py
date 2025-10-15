from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base

class MovInventario(Base):
    __tablename__ = "mov_inventario"
    id_mov = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    tipo_mov = Column(String(20), nullable=False) 
    cantidad = Column(Integer, nullable=False, default=0)
    fecha_mov = Column(DateTime, nullable=False, default=datetime.utcnow)
    descripcion = Column(String(255), nullable=True)
