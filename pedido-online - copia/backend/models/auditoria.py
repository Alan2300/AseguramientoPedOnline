from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from backend.database import Base

class Auditoria(Base):
    __tablename__ = "auditoria"
    id_auditoria = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, nullable=False)
    accion = Column(String(120), nullable=False)
    tabla_afectada = Column(String(60), nullable=False)
    fecha = Column(DateTime, server_default=func.now(), nullable=False)
