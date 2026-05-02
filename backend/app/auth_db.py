import os
import time
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker


def _normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("mysql://"):
        return raw_url.replace("mysql://", "mysql+pymysql://", 1)
    return raw_url


AUTH_DATABASE_URL = _normalize_database_url(
    os.getenv("AUTH_DATABASE_URL", "sqlite:///./auth.db")
)

engine_kwargs = {"pool_pre_ping": True}
if AUTH_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(AUTH_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


def init_auth_db() -> None:
    Base.metadata.create_all(bind=engine)


def wait_for_auth_db(max_attempts: int = 20, delay_seconds: float = 2.0) -> None:
    last_error: Exception | None = None

    for _ in range(max_attempts):
        try:
            init_auth_db()
            return
        except OperationalError as exc:
            last_error = exc
            time.sleep(delay_seconds)

    if last_error is not None:
        raise last_error


def seed_admin_user() -> None:
    from .security import hash_password

    admin_email = os.getenv("AUTH_SEED_ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("AUTH_SEED_ADMIN_PASSWORD", "")
    admin_name = os.getenv("AUTH_SEED_ADMIN_NAME", "System Admin").strip()

    if not admin_email or not admin_password:
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            existing.role = "admin"
            existing.full_name = existing.full_name or admin_name
            existing.updated_at = datetime.now(timezone.utc)
        else:
            db.add(
                User(
                    email=admin_email,
                    password_hash=hash_password(admin_password),
                    full_name=admin_name,
                    role="admin",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )
        db.commit()
    finally:
        db.close()


def seed_demo_user() -> None:
    from .security import hash_password

    user_email = os.getenv("AUTH_SEED_USER_EMAIL", "").strip().lower()
    user_password = os.getenv("AUTH_SEED_USER_PASSWORD", "")
    user_name = os.getenv("AUTH_SEED_USER_NAME", "Demo User").strip()

    if not user_email or not user_password:
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == user_email).first()
        if existing:
            existing.role = "user"
            existing.full_name = existing.full_name or user_name
            existing.updated_at = datetime.now(timezone.utc)
        else:
            db.add(
                User(
                    email=user_email,
                    password_hash=hash_password(user_password),
                    full_name=user_name,
                    role="user",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )
        db.commit()
    finally:
        db.close()


def get_auth_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()