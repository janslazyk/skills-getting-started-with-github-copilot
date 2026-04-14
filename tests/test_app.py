import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# Snapshot of the initial activities state taken at module load time
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the global activities dict to its original state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/NonExistentActivity/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_signup_already_signed_up(client):
    # Arrange — michael is already in Chess Club from the initial state
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange — michael is already in Chess Club from the initial state
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_activity_not_found(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/NonExistentActivity/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_not_signed_up(client):
    # Arrange — this email is not in Chess Club
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
