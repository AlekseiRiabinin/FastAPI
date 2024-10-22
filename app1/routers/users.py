from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
)

from sqlmodel import Session, select

from database.connection import get_session
from models.users import User

user_router = APIRouter(tags=["User"])


@user_router.get("/")
async def get_all_users(session: Session = Depends(get_session)) -> list[User]:
    statement = select(User).order_by(User.created_at)
    user = session.exec(select(statement)).all()
    return user


@user_router.get("/{user_id}")
async def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with supplied ID doesn't exist"
        )
    return user


@user_router.get("/search/", response_model=list[User])
async def search_users(query: str, session: Session = Depends(get_session)):
    statement = select(User).where(User.username.contains(query))
    users = session.exec(statement).all()
    return users


@user_router.get("/pagination/", response_model=list[User])
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    session: Session = Depends(get_session)
):
    offset = (page - 1) * page_size
    statement = select(User).offset(offset).limit(page_size)
    users = session.exec(statement).all()
    return users


@user_router.put("/{user_id}", response_model=User)
async def update_user_email(
    user_id: int,
    new_email: str,
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = new_email
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@user_router.post("/")
async def create_user(user: User, session: Session = Depends(get_session)):
    user_db = User(**user.model_dump(exclude={"id"}))

    # check on existing username
    statement_username = select(User).where(User.username == user.username)
    existing_user = session.exec(statement_username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # check on existing email
    statement_email = select(User).where(User.email == user.email)
    existing_email = session.exec(statement_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@user_router.delete("/{user_id}")
async def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with supplied ID doesn't exist"
        )
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully."}
