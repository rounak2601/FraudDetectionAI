import os
import time
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://fraud_user:fraud_pass@127.0.0.1:5433/fraud_db",
)

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5} if DATABASE_URL.startswith("postgresql") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_database(attempts: int = 15, delay_seconds: float = 2.0) -> None:
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print(f"Database connection ready (attempt {attempt}/{attempts}).")
            return
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                print(f"Database not ready (attempt {attempt}/{attempts}); retrying...")
                time.sleep(delay_seconds)
    raise RuntimeError(f"Database unavailable after {attempts} attempts: {last_error}")


def create_tables() -> None:
    # Explicit imports guarantee every table is registered in Base.metadata.
    from backend.models import audit_log, case, transaction  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
