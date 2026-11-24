"""Tests for GET /activities endpoint"""
import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all available activities"""
    # Arrange
    expected_activity_count = 9

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == expected_activity_count
    assert isinstance(activities, dict)


def test_get_activities_contains_required_fields(client):
    """Test that each activity has all required fields"""
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_name, str)
        assert required_fields.issubset(activity_data.keys())
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_participant_count_accuracy(client):
    """Test that participant counts match the actual participants list"""
    # Arrange
    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    for activity_name, activity_data in activities.items():
        participant_count = len(activity_data["participants"])
        assert participant_count <= activity_data["max_participants"]
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant


def test_get_activities_with_empty_participants(client):
    """Test that activities with no participants are handled correctly"""
    # Arrange
    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    empty_activities = [name for name, data in activities.items() if len(data["participants"]) == 0]
    assert len(empty_activities) > 0
    for activity_name in empty_activities:
        assert activities[activity_name]["participants"] == []


def test_get_activities_with_multiple_participants(client):
    """Test that activities with multiple participants display correctly"""
    # Arrange
    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    activities_with_participants = [
        name for name, data in activities.items() if len(data["participants"]) > 1
    ]
    assert len(activities_with_participants) > 0
    for activity_name in activities_with_participants:
        assert len(activities[activity_name]["participants"]) > 1
