# tests/test_app.py
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    # Arrange: No specific setup needed as activities are predefined
    
    # Act: Make GET request to /activities
    response = client.get("/activities")
    
    # Assert: Check status and response structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # Arrange: Use an email not already signed up
    
    # Act: Make POST request to signup
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    
    # Assert: Check success response
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]

def test_signup_duplicate_activity():
    # Arrange: Sign up for an activity first
    client.post("/activities/Programming%20Class/signup?email=duplicate@mergington.edu")
    
    # Act: Attempt to sign up again for the same activity
    response = client.post("/activities/Programming%20Class/signup?email=duplicate@mergington.edu")
    
    # Assert: Check error for duplicate signup
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_nonexistent_activity():
    # Arrange: No setup needed
    
    # Act: Try to sign up for a non-existent activity
    response = client.post("/activities/Nonexistent/signup?email=nonexistent@mergington.edu")
    
    # Assert: Check 404 error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    # Arrange: Sign up first
    client.post("/activities/Gym%20Class/signup?email=unregister@mergington.edu")
    
    # Act: Unregister the participant
    response = client.delete("/activities/Gym%20Class/signup?email=unregister@mergington.edu")
    
    # Assert: Check success response
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]

def test_unregister_not_signed_up():
    # Arrange: No setup needed
    
    # Act: Try to unregister a non-participant
    response = client.delete("/activities/Chess%20Club/signup?email=notsigned@mergington.edu")
    
    # Assert: Check error response
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_nonexistent_activity():
    # Arrange: No setup needed
    
    # Act: Try to unregister from a non-existent activity
    response = client.delete("/activities/Nonexistent/signup?email=nonexistent2@mergington.edu")
    
    # Assert: Check 404 error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]