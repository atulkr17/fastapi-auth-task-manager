from fastapi import FastAPI , Depends, HTTPException, status , APIRouter
from sqlalchemy.orm import Session
from src.db_services.connect_db import get_db

from src.schemas.user import(
    UserCreate,
    UserUpdate,
    UserResponse,
)

from src.crud.user import (
    create_user,
    get_users,
    get_user_by_id,
    update_user,
    delete_user,
)

router = APIRouter(
    prefix = '/users',
    tags = ['Users'],
)

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.get('/', response_model = list[UserResponse])
def get_all_user(db: Session = Depends(get_db)):

    return get_users(db)

@router.get('/{user_id}', response_model=UserResponse,)
def get_user_id(user_id , db: Session = Depends(get_db)):
    return get_user_by_id(user_id , db)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user_endpoint(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = update_user(
        db,
        user_id,
        user_data,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = delete_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return None