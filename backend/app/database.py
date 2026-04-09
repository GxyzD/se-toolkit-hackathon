from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Auto-detect database: PostgreSQL if available, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./students.db")

# Check if PostgreSQL URL
if DATABASE_URL.startswith("postgresql"):
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        print(f"✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"⚠️  PostgreSQL not available ({e}), falling back to SQLite")
        DATABASE_URL = "sqlite:///./students.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print(f"✅ Using SQLite database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()