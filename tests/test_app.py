from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def _remove_participant_if_present(activity_name: str, email: str) -> None:
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)


def _add_participant_if_missing(activity_name: str, email: str) -> None:
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)


def test_root_redirects_to_static_index():
    # Arrange
    path = "/"

    # Act
    response = client.get(path, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure():
    # Arrange
    path = "/activities"

    # Act
    response = client.get(path)

    # Assert
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, dict)
    assert payload

    first_activity = next(iter(payload.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity


def test_signup_success_returns_exact_message():
    # Arrange
    activity_name = "Chess Club"
    email = "new.student.signup@mergington.edu"
    _remove_participant_if_present(activity_name, email)

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    _remove_participant_if_present(activity_name, email)


def test_signup_unknown_activity_returns_404_with_exact_detail():
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_duplicate_returns_400_with_exact_detail():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_success_returns_exact_message():
    # Arrange
    activity_name = "Chess Club"
    email = "remove.student@mergington.edu"
    _add_participant_if_missing(activity_name, email)

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}


def test_unregister_unknown_activity_returns_404_with_exact_detail():
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_missing_participant_returns_404_with_exact_detail():
    # Arrange
    activity_name = "Chess Club"
    email = "not.registered@mergington.edu"
    _remove_participant_if_present(activity_name, email)

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found for this activity"}
