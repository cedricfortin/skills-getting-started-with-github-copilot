"""Tests for DELETE /activities/{activity_name}/unregister endpoint"""
import pytest


def test_unregister_existing_participant_success(client):
    """Test that an existing participant can be successfully unregistered"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Verify participant exists before unregister
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]

    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_rejected(client):
    """Test that unregistering a non-existent participant is rejected"""
    # Arrange
    activity_name = "Programming Class"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_from_nonexistent_activity_returns_404(client):
    """Test that unregistering from a non-existent activity returns 404"""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "alex@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_only_participant_in_activity(client):
    """Test that the only participant can be unregistered"""
    # Arrange
    activity_name = "Drama Club"
    email = "sole_participant@mergington.edu"

    # First, add a participant to an empty activity
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Verify only one participant
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert len(activities[activity_name]["participants"]) == 1
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 200

    # Verify activity has no participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert len(activities[activity_name]["participants"]) == 0


def test_unregister_one_of_multiple_participants(client):
    """Test that one participant can be removed when multiple are signed up"""
    # Arrange
    activity_name = "Programming Class"
    email_to_remove = "emma@mergington.edu"
    other_participant = "sophia@mergington.edu"

    # Verify both participants exist
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email_to_remove in activities[activity_name]["participants"]
    assert other_participant in activities[activity_name]["participants"]
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email_to_remove}",
        headers={"accept": "application/json"}
    )

    # Assert
    assert response.status_code == 200

    # Verify correct participant was removed and other remains
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email_to_remove not in activities[activity_name]["participants"]
    assert other_participant in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1


def test_unregister_then_rejoin(client):
    """Test that a participant can unregister and then sign up again"""
    # Arrange
    activity_name = "Soccer Club"
    email = "rejoiner@mergington.edu"

    # Sign up initially
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Verify signed up
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]

    # Act - Unregister
    response1 = client.delete(
        f"/activities/{activity_name}/unregister?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert - Unregistered successfully
    assert response1.status_code == 200

    # Verify unregistered
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]

    # Act - Sign up again
    response2 = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"accept": "application/json"}
    )

    # Assert - Signed up again successfully
    assert response2.status_code == 200
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_unregister_increases_availability(client):
    """Test that unregistering a participant increases available spots"""
    # Arrange
    activity_name = "Basketball Team"
    email_to_remove = "player1@mergington.edu"
    email_to_add = "new_player@mergington.edu"

    # First, fill the activity to capacity
    activities_response = client.get("/activities")
    activity_data = activities_response.json()[activity_name]
    max_capacity = activity_data["max_participants"]

    # Add participants
    for i in range(max_capacity):
        client.post(f"/activities/{activity_name}/signup?email=player{i}@mergington.edu")

    # Verify at capacity
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert len(activities[activity_name]["participants"]) == max_capacity

    # Act - Unregister one participant
    response1 = client.delete(
        f"/activities/{activity_name}/unregister?email=player0@mergington.edu",
        headers={"accept": "application/json"}
    )

    # Assert - Spot is now available
    assert response1.status_code == 200
    response2 = client.post(
        f"/activities/{activity_name}/signup?email={email_to_add}",
        headers={"accept": "application/json"}
    )
    assert response2.status_code == 200
