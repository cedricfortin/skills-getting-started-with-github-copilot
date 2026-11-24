"""Tests for POST /activities/{activity_name}/signup endpoint"""
import pytest


def test_signup_new_student_success(client):
    """Test that a new student can successfully sign up for an activity"""
    # Arrange
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email_rejected(client):
    """Test that signing up twice with the same email is rejected"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity_returns_404(client):
    """Test that signing up for a non-existent activity returns 404"""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "alex@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_at_max_capacity_rejected(client):
    """Test that signing up for a full activity is rejected"""
    # Arrange
    activity_name = "Gym Class"
    # Gym Class has max_participants=30, let's fill it up
    email_to_reject = "new_student@mergington.edu"

    # First, fill the activity to capacity
    activities_response = client.get("/activities")
    activity_data = activities_response.json()[activity_name]
    current_participants = len(activity_data["participants"])
    max_capacity = activity_data["max_participants"]

    # Fill remaining spots
    for i in range(current_participants, max_capacity):
        test_email = f"filler{i}@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Act - Try to sign up when at capacity
    response = client.post(
        f"/activities/{activity_name}/signup?email={email_to_reject}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 400
    assert "maximum capacity" in response.json()["detail"]
    
    # Verify the email was not added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email_to_reject not in activities[activity_name]["participants"]


def test_signup_last_available_spot(client):
    """Test that signing up for the last available spot succeeds"""
    # Arrange
    activity_name = "Soccer Club"
    max_capacity = 22

    # Fill all but one spot
    for i in range(max_capacity - 1):
        client.post(f"/activities/{activity_name}/signup?email=filler{i}@mergington.edu")

    last_student_email = "last_student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={last_student_email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 200
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert last_student_email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == max_capacity


def test_signup_to_empty_activity(client):
    """Test that signing up to an activity with no participants succeeds"""
    # Arrange
    activity_name = "Art Club"  # Has no participants initially
    email = "artist@mergington.edu"

    # Verify activity is empty
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert len(activities[activity_name]["participants"]) == 0

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 200
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == 1


def test_signup_email_format_accepted(client):
    """Test that valid email formats are accepted"""
    # Arrange
    activity_name = "Drama Club"
    valid_emails = [
        "simple@mergington.edu",
        "user.name@mergington.edu",
        "user+tag@mergington.edu",
        "first.last.middle@mergington.edu"
    ]

    # Act & Assert
    for email in valid_emails:
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"accept": "application/json"}
        )
        assert response.status_code == 200, f"Failed for email: {email}"
