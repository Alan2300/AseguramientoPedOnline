from sqlalchemy import Column, Integer, String
from backend.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(180), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    id_rol = Column(Integer, nullable=False, default=2)
