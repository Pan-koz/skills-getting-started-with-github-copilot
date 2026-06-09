import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    new_email = "newstudent@mergington.edu"
    activity_name = urllib.parse.quote("Chess Club")

    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for Chess Club"

    response = client.get("/activities")
    assert response.status_code == 200
    activity = response.json()["Chess Club"]
    assert new_email in activity["participants"]


def test_duplicate_signup_returns_400():
    existing_email = "michael@mergington.edu"
    activity_name = urllib.parse.quote("Chess Club")

    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_them_from_activity():
    participant_email = "michael@mergington.edu"
    activity_name = urllib.parse.quote("Chess Club")

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant_email} from Chess Club"

    response = client.get("/activities")
    assert response.status_code == 200
    activity = response.json()["Chess Club"]
    assert participant_email not in activity["participants"]


def test_unregister_nonexistent_participant_returns_404():
    participant_email = "ghost@mergington.edu"
    activity_name = urllib.parse.quote("Chess Club")

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"
