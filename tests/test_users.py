from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base, get_db
from app.main import app
from app.schemas import UserOut
from app.config import settings
from alembic import command

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/fastapi_test'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit = False, autoflush= False , bind= engine)

# Base.metadata.create_all(bind = engine)

# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app.dependency_overrides[get_db] = override_get_db

# client = TestClient(app)

@pytest.fixture
def session():
    Base.metadata.drop_all(bind = engine)
    Base.metadata.create_all(bind = engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    # run our code before we run our test 
    # command.upgrade("head")
    yield TestClient(app)
    # command.downgrade("base")
    # run our code after our test finishes

def test_root(client):
    res = client.get("/")
    # print(res.json().get('message'))
    assert res.status_code == 200
    assert res.json().get("message") == "Hello world"


def test_create_user(client):
    res = client.post(
        "/users", json={"email": "hello123@gmail.com", "password": "password123"}
    )

    new_user = UserOut(**res.json())
    # print(res.json())
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201
