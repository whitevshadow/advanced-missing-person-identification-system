from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth_db import User, get_auth_db
from ..schemas import TokenResponse, UserCreate, UserLogin, UserRead, UserRoleUpdate
from ..security import create_access_token, get_current_user, hash_password, require_roles, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_auth_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role="user",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_user_read(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_auth_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(subject=str(user.id), role=user.role)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead)
def read_me(current_user=Depends(get_current_user)):
    return _to_user_read(current_user)


@router.get("/users", response_model=list[UserRead])
def list_users(current_user=Depends(require_roles("admin")), db: Session = Depends(get_auth_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [_to_user_read(user) for user in users]


@router.patch("/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    current_user=Depends(require_roles("admin")),
    db: Session = Depends(get_auth_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = payload.role
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return _to_user_read(user)