from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    original_state = deepcopy(app_module.activities)
    test_client = TestClient(app_module.app)

    yield test_client

    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_state))


def test_unregistered_student_is_removed_from_activity(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "newstudent@mergington.edu"
    activity = app_module.activities[activity_name]

    if email in activity["participants"]:
        activity["participants"].remove(email)

    # Act: sign the student up for the activity
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: the student was added successfully
    assert signup_response.status_code == 200
    assert email in activity["participants"]

    # Arrange: the student is now registered and ready to be removed
    assert email in activity["participants"]

    # Act: remove the student from the activity
    delete_response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert: the student was removed successfully
    assert delete_response.status_code == 200
    assert email not in activity["participants"]


def test_student_cannot_sign_up_twice_for_same_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activity = app_module.activities[activity_name]

    assert email in activity["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert activity["participants"].count(email) == 1


def test_sign_up_for_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_removing_nonexistent_participant_returns_404(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "notregistered@mergington.edu"
    activity = app_module.activities[activity_name]

    assert email not in activity["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert email not in activity["participants"]


def test_removing_participant_from_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
