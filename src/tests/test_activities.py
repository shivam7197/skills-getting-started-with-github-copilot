"""
Tests for the Mergington High School Activities API.

Tests cover all endpoints:
- GET / (redirect to index)
- GET /activities (list all activities)
- POST /activities/{activity_name}/signup (register a student)
"""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that the root endpoint redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesListEndpoint:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9
        
        # Verify some key activities are present
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Art Studio" in activities
    
    def test_get_activities_includes_correct_fields(self, client):
        """Test that activity objects have all required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        # Check structure of an activity
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_includes_initial_participants(self, client):
        """Test that activities include their initial participants."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have initial participants
        chess_club = activities["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 2


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_successful_signup_adds_participant(self, client):
        """Test that a valid signup adds the email to participants."""
        response = client.post(
            "/activities/Chess Club/signup?email=newemail@mergington.edu",
            follow_redirects=False
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "newemail@mergington.edu" in result["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newemail@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        response = client.post(
            "/activities/Fake Activity/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()
    
    def test_duplicate_signup_returns_400(self, client):
        """Test that signing up twice for the same activity returns 400."""
        email = "newemail@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 400
        result = response2.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()
    
    def test_signup_with_url_encoded_email(self, client):
        """Test that email with special characters is properly handled."""
        # Email with + that might be URL-encoded
        email = "student+test@mergington.edu"
        response = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test that activity names with spaces are properly handled."""
        # Activity name with spaces should work when passed to the endpoint
        response = client.post(
            "/activities/Basketball Team/signup?email=athlete@mergington.edu"
        )
        
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "athlete@mergington.edu" in activities["Basketball Team"]["participants"]
    
    def test_signup_response_contains_correct_message(self, client):
        """Test that the response message includes the email and activity name."""
        email = "student@mergington.edu"
        activity = "Art Studio"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        result = response.json()
        assert email in result["message"]
        assert activity in result["message"] or "Signed up" in result["message"]
