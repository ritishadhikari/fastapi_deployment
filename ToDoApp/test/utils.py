"""
This Python  Script contains all the reusable components that will be shared
among all the test scripts
"""

from sqlalchemy import create_engine,text
from sqlalchemy.pool import StaticPool,QueuePool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from fastapi.testclient import TestClient
import pytest
from ..models import Todos, Users
from ..main import app
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL="sqlite:///./testdb.db"

engine=create_engine(
    url=SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread":False
        },
    poolclass=QueuePool
    )

TestingSessionLocal=sessionmaker(
                    bind=engine,
                    autoflush=False,
                    autocommit=False)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    yield {
        'username':'ritishadhikaritest',
        'id':1,
        'user_role':'admin'
        }
    
client=TestClient(app=app)

@pytest.fixture
def test_todo():
    todo=Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1
        )
    db=TestingSessionLocal()
    db.add(instance=todo)
    db.commit()
    yield db

    with engine.connect() as connection:
        connection.execute(statement=text(text="DELETE FROM todos"))
        connection.commit()

@pytest.fixture
def test_user():
    user=Users(
        email='ritishadhikaritest@email.com',  #
        username='ritishadhikaritest',  #
        first_name='ritish',  #
        last_name='adhikaritest',  #
        hashed_password=bcrypt_context.hash(secret='ritishadhikaritest'),  #
        role='admin',  #
        phone_number='8665537373',  #
    )
    db=TestingSessionLocal()
    db.add(instance=user)
    db.commit()
    yield user
    
    with engine.connect() as connection:
        connection.execute(statement=text(text="DELETE FROM users;")) 
        connection.commit()

