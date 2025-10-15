import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

def _uri():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    pw = os.getenv("DB_PASS", "")
    db = os.getenv("DB_NAME", "pedido_online_db")
    return f"mysql+mysqlconnector://{user}:{pw}@{host}/{db}"

engine = create_engine(_uri(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
