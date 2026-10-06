from sqlalchemy import inspect
from src.model.user import USERS

from src.db_services.connect_db import engine

inspector = inspect(engine)


# if inspector.has_table(USERS):
if inspector.has_table(USERS.__tablename__):
    print('user table is exists')
    print(f"Table name: {USERS.__tablename__}")
    print("Columns:")

    for column in USERS.__table__.columns:
        print(f"- {column.name}: {column.type}")
else:
    print("user table is not exists")    
