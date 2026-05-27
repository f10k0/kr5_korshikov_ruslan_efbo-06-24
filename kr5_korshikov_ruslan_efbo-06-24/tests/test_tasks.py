import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import storage

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_storage():
    storage.clear()
    yield

def test_create_task_success():
    response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Some desc", "status": "todo", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["owner_id"] == 10
    assert "id" in data

def test_create_task_title_too_short():
    response = client.post(
        "/tasks/",
        json={"title": "ab", "priority": 3, "status": "todo"},
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 422

def test_create_task_no_user_header():
    response = client.post("/tasks/", json={"title": "Task", "priority": 3, "status": "todo"})
    assert response.status_code == 401

def test_user_sees_only_own_tasks():
    client.post("/tasks/", json={"title": "User10 task1", "priority": 3, "status": "todo"}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "User10 task2", "priority": 4, "status": "in_progress"}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "User20 task", "priority": 2, "status": "done"}, headers={"X-User-Id": "20"})
    resp = client.get("/tasks/", headers={"X-User-Id": "10"})
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 2
    assert all(t["owner_id"] == 10 for t in tasks)

def test_filter_tasks_by_status_and_min_priority():
    storage.clear()
    r1 = client.post("/tasks/", json={"title": "task1", "priority": 2, "status": "todo"}, headers={"X-User-Id": "10"})
    r2 = client.post("/tasks/", json={"title": "task2", "priority": 4, "status": "todo"}, headers={"X-User-Id": "10"})
    r3 = client.post("/tasks/", json={"title": "task3", "priority": 5, "status": "done"}, headers={"X-User-Id": "10"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 201
    resp = client.get("/tasks/?status=todo", headers={"X-User-Id": "10"})
    assert len(resp.json()) == 2
    resp = client.get("/tasks/?min_priority=4", headers={"X-User-Id": "10"})
    assert len(resp.json()) == 2
    resp = client.get("/tasks/?status=todo&min_priority=4", headers={"X-User-Id": "10"})
    assert len(resp.json()) == 1

def test_update_task_status_success():
    create_resp = client.post("/tasks/", json={"title": "To update", "priority": 3, "status": "todo"}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    patch_resp = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}, headers={"X-User-Id": "10"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "done"

def test_get_other_users_task_404():
    create_resp = client.post("/tasks/", json={"title": "Own", "priority": 3, "status": "todo"}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert resp.status_code == 404

def test_delete_task_success():
    create_resp = client.post("/tasks/", json={"title": "To delete", "priority": 3, "status": "todo"}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    del_resp = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert del_resp.status_code == 204
    get_resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_resp.status_code == 404