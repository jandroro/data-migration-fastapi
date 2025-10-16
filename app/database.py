from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import config

# Create engine
engine = create_engine(
    config.get_database_url(),
    echo=config.DB_ECHO,
    connect_args={"check_same_thread": False}
    if config.DATABASE_URL and "sqlite" in config.DATABASE_URL
    else {},
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Connection health check
def check_database_connection():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False
