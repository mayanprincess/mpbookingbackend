from sqlalchemy import create_engine, MetaData
from src.core.config import settings
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    f"mysql+pymysql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}",
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
