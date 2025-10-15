from sqlalchemy import Column, Integer, ForeignKey
from backend.database import Base

class Inventario(Base):
    __tablename__ = "inventario"
    id_inventario = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad_actual = Column(Integer, nullable=False, default=0)
