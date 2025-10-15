from sqlalchemy import Column, Integer, String, Numeric
from backend.database import Base

class Producto(Base):
    __tablename__ = "productos"
    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(500), nullable=True)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    imagen = Column(String(255), nullable=True)
