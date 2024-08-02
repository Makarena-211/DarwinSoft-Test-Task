import pytest 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import sys
import os

from app import database, main


test_db_url = "postgresql+psycopg2://postgres:password@127.0.0.1:5433/test_postgres"
engine =  create_engine(test_db_url)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database.Base.metadata.create_all(bind=engine)

class CustomTestClient(TestClient):
    def delete_with_payload(self, **kwargs):
        return self.request(method="DELETE", **kwargs)
    
@pytest.fixture(scope='function')
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.commit()
    connection.close()

@pytest.fixture(scope='function')
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    main.app.dependency_overrides[database.get_db] = override_get_db
    with CustomTestClient(main.app) as test_client:
        yield test_client

    
@pytest.fixture()
def user_payload():
    return {
        "username": "user1",
        "password": "password1"
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
