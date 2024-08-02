import pytest 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import sys
import os

from sqlalchemy.sql import text
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database, main
from auth import get_password_hash



test_db_url = "postgresql+psycopg2://postgres:password@127.0.0.1:5433/test_postgres"

class CustomTestClient(TestClient):
    def delete_with_payload(self, **kwargs):
        return self.request(method="DELETE", **kwargs)

@pytest.fixture(scope='session')
def test_db():
    engine = create_engine(test_db_url)
    database.Base.metadata.create_all(bind=engine)
    
    yield engine
    database.Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def db_session(test_db):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = SessionLocal()
    yield session
    session.commit()
    session.close()

@pytest.fixture(scope='session')
def add_admin_user(test_db):
    with test_db.connect() as connection:
        result = connection.execute(
                text("SELECT COUNT(*) FROM users WHERE username = :username"),
                {"username": "admin1"}
            )
        count = result.scalar()
            
        if count == 0:
            hashed_password = get_password_hash('admin1')
            connection.execute(
                text("INSERT INTO users (username, hashed_password, role) VALUES (:username, :password, :role)"),
                {"username": "admin1", "password": hashed_password, "role": "admin"}
            )
            connection.commit()

@pytest.fixture(scope='function')
def test_client(test_db, add_admin_user):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = SessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    main.app.dependency_overrides[database.get_db] = override_get_db
    
    with CustomTestClient(main.app) as client:
        yield client

@pytest.fixture()
def user_payload():
    return {
        "username": "user1",
        "password": "password1"
    }

@pytest.fixture()
def login_user_payload():
    return {
        "grant_type": "password",
        "username": "user1",
        "password": "password1",
        "scope": None,
        "client_id":"string",
        "client_secret":"string"
    }

@pytest.fixture()
def task_payload():
    return {
        "name": "task1",
        "description": "task1",
        "deadline": "2025-08-01",
        "done": False
    }

@pytest.fixture()
def task_update_payload():
    return {
        "name": "task1",
        "description": "task1",
        "deadline": "2025-08-01",
        "done": True
    }

@pytest.fixture()
def permission_update_payload():
    return {
        "task_id": 0,
        "user_id": 0,
        "can_read": True,
        "can_update": True,
        "can_delete": True,
        "can_write": True
    }
