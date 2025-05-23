from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_student():
    response = client.post("/students/", json={"name": "Test Student"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Student"

def test_get_all_students():
    response = client.get("/students/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_task_for_student():
    student = client.post("/students/", json={"name": "TaskOwner"}).json()
    student_id = student["id"]

    task_data = {
        "description": "Test Task",
        "complete": False,
        "student_id": student_id
    }
    response = client.post(f"/students/{student_id}/tasks/", json=task_data)
    assert response.status_code == 200
    assert response.json()["description"] == "Test Task"
    assert response.json()["student_id"] == student_id

def test_get_tasks_for_student():
    student = client.post("/students/", json={"name": "TaskChecker"}).json()
    student_id = student["id"]

    client.post(f"/students/{student_id}/tasks/", json={
        "description": "Another Task",
        "complete": False,
        "student_id": student_id
    })

    response = client.get(f"/students/{student_id}/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
