"""
Backend tests for Mergington High School activities API
Uses fastapi.testclient.TestClient and pytest with AAA pattern
"""

from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Arrange-Act-Assert: Verify activities endpoint returns all activities"""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Debate Team",
            "Science Club",
            "Art Studio",
            "Music Ensemble"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        for activity in expected_activities:
            assert activity in activities
            assert "description" in activities[activity]
            assert "schedule" in activities[activity]
            assert "max_participants" in activities[activity]
            assert "participants" in activities[activity]

    def test_get_activities_returns_participants_list(self):
        """Arrange-Act-Assert: Verify participants are returned as a list"""
        # Arrange
        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
            assert len(activity_data["participants"]) > 0


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self):
        """Arrange-Act-Assert: Successfully sign up a new participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_participant_fails(self):
        """Arrange-Act-Assert: Reject signup for already registered participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up in seed data

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self):
        """Arrange-Act-Assert: Reject signup for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_participant_appears_in_activities_list(self):
        """Arrange-Act-Assert: Verify new participant appears in activities list after signup"""
        # Arrange
        activity_name = "Basketball Team"
        email = "testuser@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert signup_response.status_code == 200
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_existing_participant_success(self):
        """Arrange-Act-Assert: Successfully unregister an existing participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"  # Already in seed data

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_nonexistent_participant_fails(self):
        """Arrange-Act-Assert: Reject unregister for non-existent participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self):
        """Arrange-Act-Assert: Reject unregister from non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_participant_removed_from_activities_list(self):
        """Arrange-Act-Assert: Verify participant is removed from activities list after unregister"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already in seed data

        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert unregister_response.status_code == 200
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]
