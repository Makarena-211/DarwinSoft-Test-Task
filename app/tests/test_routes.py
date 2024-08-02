import pytest
from fastapi.testclient import TestClient
from fastapi import status
from conftest import test_client, user_payload, task_payload, login_user_payload, task_update_payload
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import schemas, models
from auth import verify_password

def test_register_user(test_client, user_payload, db_session):
    print(f"payload - {user_payload}")
    response = test_client.post('/register', json=user_payload)
    assert response.status_code == status.HTTP_200_OK
    db_session.commit()
    db_user = db_session.query(models.User).filter(models.User.username == user_payload["username"]).first()
    assert db_user is not None
    assert db_user.username == user_payload["username"]
    assert verify_password(user_payload["password"], db_user.hashed_password)

    db_permission = db_session.query(models.Permission).filter(models.Permission.user_id == db_user.id).first()
    assert db_permission is not None
    assert db_permission.user_id == db_user.id
    assert db_permission.can_read == True
    assert db_permission.can_write == False
    assert db_permission.can_update == False
    assert db_permission.can_delete == False


@pytest.fixture
def token(test_client):
    response = test_client.post(
        "/token",
        data={"username": "user1", "password": "password1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]



def test_login_for_access_token(test_client):
    response = test_client.post(
        "/token",
        data={"username": "user1", "password": "password1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.fixture
def token_admin(test_client):
    response = test_client.post(
        "/token",
        data={"username": "admin1", "password": "admin1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]

def test_login_for_access_token_admin(test_client):
    response = test_client.post(
        "/token",
        data={"username": "admin1", "password": "admin1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_update_permission(test_client, token_admin, db_session, permission_update_payload):
    first_user_id = db_session.query(models.User.id).filter(models.User.role == "user").order_by(models.User.id).first()
    if first_user_id:
        first_user_id = first_user_id[0]  
        permission = db_session.query(models.Permission).filter(models.Permission.user_id == first_user_id).first()
        permission_id = permission.id
        permission_update_payload['task_id'] = None
        permission_update_payload['user_id'] = first_user_id
    response = test_client.put(
        f"/tasks/{permission_id}/permissions",
        json=permission_update_payload,
        headers={"Authorization": f"Bearer {token_admin}"}
    )

    assert response.status_code == 200
    updated_permission = response.json()
    assert updated_permission["can_read"] == permission_update_payload["can_read"]
    assert updated_permission["can_write"] == permission_update_payload["can_write"]
    assert updated_permission["can_update"] == permission_update_payload["can_update"]
    assert updated_permission["can_delete"] == permission_update_payload["can_delete"]



def test_create_task(test_client, token, task_payload):
    response = test_client.post(
        "/post",
        json=task_payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    created_task = response.json()
    assert created_task["name"] == task_payload["name"]
    assert created_task["description"] == task_payload["description"]
    assert created_task["deadline"] == task_payload["deadline"]
    assert created_task["done"] == task_payload["done"]

def test_get_tasks(test_client, token):
    response = test_client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    print(data)

def test_update_task(test_client, token, task_update_payload):
    task_id = 1
    response = test_client.put(url=f"/update/{task_id}", json=task_update_payload, headers={"Authorization": f"Bearer {token}"})
    created_task = response.json()
    assert response.status_code == 200
    print(created_task)
    assert created_task["name"] == task_update_payload["name"]
    assert created_task["description"] == task_update_payload["description"]
    assert created_task["deadline"] == task_update_payload["deadline"]
    assert created_task["done"] == task_update_payload["done"]




def test_delete_task(test_client, token):
    task_id = 1
    response = test_client.delete(url=f"/delete/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
