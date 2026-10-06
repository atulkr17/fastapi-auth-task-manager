from src.model.user import USERS
from sqlalchemy.orm import Session
from src.schemas.user import(

    UserCreate, UserUpdate
)
from src.auth.security import hash_password

def get_users(db: Session):
    users = db.query(USERS).all()
    return users

def get_user_by_id(db:Session, user_id: int):
    user = db.query(USERS).filter(USERS.id == user_id).first()
    return user

# def create_user(db: Session, user: UserUpdate):
#     new_user = USERS(
#         name = user.name,
#         email=user.email,
#         password=user.password,
#         medialname=user.medialname,
#     )

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

def create_user( db: Session,  name: str,email: str,  password: str):
    hashed_password = hash_password(password)
    
    new_user = USERS(
        name=name,
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def update_user(
        db:Session,
        user_id: int,
        user_data:UserUpdate
):
    user = get_user_by_id(db,user_id)
    if user is None:
        return {'message': 'user not found'}

    update_data = user_data.model_dump(exclude_unset= True)

    for field , value in update_data.items():
        setattr(user,field, value)

    db.commit()
    db.refresh(user)
    return user    

def delete_user(db: Session , user_id: int):
    user = get_user_by_id(db, user_id)
    if user is None:
        return {'message': 'user not found'}

    db.delete(user)
    db.commit()
    return {'message': 'user deleted successfully'}


def get_user_by_email(db: Session, email: str):
    """Find the user using email address"""

    return (
        db.query(USERS)
        .filter(USERS.email == email)
        .first()
    )