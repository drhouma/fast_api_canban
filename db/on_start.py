from pwdlib import PasswordHash

from app.db.database import Base, sync_engine, sessionLocal
from app.models.user import User


password_hash = PasswordHash.recommended()

def create_tables():
    Base.metadata.create_all(sync_engine)


def delete_tables():
    Base.metadata.drop_all(sync_engine)

def insert_data():
    session = sessionLocal()
    pwd=password_hash.hash("123321")
    session.add(User(email="andre@mail.ru", username="Andre", hashed_password=pwd))
    session.commit()
    session.close()
