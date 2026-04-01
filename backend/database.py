from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Docker-compose'daki ayarlara uygun bağlantı URL'si
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:tidesense_secret@localhost:5432/tidesense"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Veritabanı oturumu oluşturma yardımcısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
