"""Tests for Mergington High School Activities API using AAA (Arrange-Act-Assert) pattern"""
import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: No special setup needed (fixture handles it)
        Act: Make GET request to /activities
        Assert: Verify all activities are returned with correct structure
        """
        # Arrange - handled by reset_activities fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 3

    def test_get_activities_contains_participant_info(self, client):
        """
        Arrange: Activities fixture has sample participants
        Act: Get activities
        Assert: Verify participants list is included
        """
        # Arrange - handled by reset_activities fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        chess_club = response.json()["Chess Club"]
        assert "participants" in chess_club
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 2


class TestSignup:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_successful(self, client):
        """
        Arrange: Student email not yet registered for activity
        Act: Post signup request
        Assert: Student added to participants list
        """
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        updated_activity = client.get("/activities").json()[activity_name]
        assert email in updated_activity["participants"]
        assert len(updated_activity["participants"]) == initial_count + 1

    def test_signup_duplicate_student_returns_400(self, client):
        """
        Arrange: Student already registered for activity
        Act: Attempt to signup again
        Assert: Returns 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Activity does not exist
        Act: Attempt to signup for non-existent activity
        Assert: Returns 404 error
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_different_activities(self, client):
        """
        Arrange: Student signing up for multiple activities
        Act: Post signup requests for different activities
        Assert: Student appears in all activities
        """
        # Arrange
        email = "bob@mergington.edu"
        activities_list = ["Chess Club", "Programming Class"]
        
        # Act
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Assert
        all_activities = client.get("/activities").json()
        for activity in activities_list:
            assert email in all_activities[activity]["participants"]


class TestUnregister:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_successful(self, client):
        """
        Arrange: Student is registered for activity
        Act: Post delete request to unregister
        Assert: Student removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        updated_activity = client.get("/activities").json()[activity_name]
        assert email not in updated_activity["participants"]

    def test_unregister_non_participant_returns_400(self, client):
        """
        Arrange: Student not registered for activity
        Act: Attempt to unregister
        Assert: Returns 400 error
        """
        # Arrange
        activity_name = "Programming Class"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Activity does not exist
        Act: Attempt to unregister from non-existent activity
        Assert: Returns 404 error
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_then_signup_again_successful(self, client):
        """
        Arrange: Student unregisters then attempts to register again
        Act: Unregister, then signup
        Assert: Both operations succeed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Unregister
        response_delete = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response_delete.status_code == 200
        
        # Act - Signup again
        response_signup = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response_signup.status_code == 200
        activity_data = client.get("/activities").json()[activity_name]
        assert email in activity_data["participants"]
