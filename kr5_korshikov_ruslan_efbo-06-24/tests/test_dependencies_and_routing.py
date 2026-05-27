import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import storage

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_storage():
    storage.clear()
    yield

def test_users_me_returns_current_user():
    resp = client.get("/users/me", headers={"X-User-Id": "42", "X-User-Role": "admin"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 42
    assert data["role"] == "admin"

def test_no_user_header_401():
    resp = client.get("/users/me")
    assert resp.status_code == 401

def test_admin_stats_forbidden_for_user():
    resp = client.get("/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert resp.status_code == 403

def test_admin_stats_success():
    storage.clear()
    r1 = client.post("/tasks/", json={"title": "task1", "priority": 1, "status": "todo"}, headers={"X-User-Id": "10"})
    r2 = client.post("/tasks/", json={"title": "task2", "priority": 2, "status": "done"}, headers={"X-User-Id": "10"})
    r3 = client.post("/tasks/", json={"title": "task3", "priority": 3, "status": "todo"}, headers={"X-User-Id": "20"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 201
    resp = client.get("/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tasks"] == 3
    assert data["by_status"]["todo"] == 2
    assert data["by_status"]["done"] == 1

def test_user_cannot_delete_other_task():
    create_resp = client.post("/tasks/", json={"title": "user10 task", "priority": 3, "status": "todo"}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    resp = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert resp.status_code == 404

def test_admin_can_delete_any_task():
    create_resp = client.post("/tasks/", json={"title": "any task", "priority": 3, "status": "todo"}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    resp = client.delete(f"/admin/tasks/{task_id}", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert resp.status_code == 204
    get_resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_resp.status_code == 404