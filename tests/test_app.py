from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_unregistered_student_is_removed_from_activity():
    activity_name = "Soccer Team"
    email = "newstudent@mergington.edu"

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    delete_response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert delete_response.status_code == 200
    assert email not in activities[activity_name]["participants"]
