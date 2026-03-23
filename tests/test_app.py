# tests/test_app.py
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

@pytest.fixture
def test_email():
    return "test@example.com"

@pytest.fixture
def activity_name():
    return "Chess Club"

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

def test_signup_success(test_email):
    # Arrange: Use an email not already signed up
    
    # Act: Make POST request to signup
    response = client.post(f"/activities/Chess%20Club/signup?email={test_email}")
    
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

def test_root_redirect():
    # Arrange: No specific setup needed
    
    # Act: Make GET request to root endpoint
    response = client.get("/")
    
    # Assert: Check that it serves the static HTML (redirect followed or direct serve)
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()

def test_api_docs_accessible():
    # Arrange: No setup needed
    
    # Act: Make GET request to /docs
    response = client.get("/docs")
    
    # Assert: Check that docs are accessible
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_api_redoc_accessible():
    # Arrange: No setup needed
    
    # Act: Make GET request to /redoc
    response = client.get("/redoc")
    
    # Assert: Check that redoc is accessible
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_signup_at_max_capacity():
    # Arrange: Fill up Chess Club to max capacity (max 12, currently 2)
    activity = "Chess%20Club"
    for i in range(10):
        email = f"student{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act: Try to sign up one more student
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    
    # Assert: Check that signup is rejected due to capacity
    assert response.status_code == 400
    data = response.json()
    assert "full" in data["detail"].lower() or "capacity" in data["detail"].lower()

def test_multiple_signups_same_activity():
    # Arrange: Get initial participant count for Basketball Team
    activity = "Basketball%20Team"
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity.replace("%20", " ")]["participants"])
    
    # Act: Sign up two students for the same activity
    client.post(f"/activities/{activity}/signup?email=multi1@mergington.edu")
    client.post(f"/activities/{activity}/signup?email=multi2@mergington.edu")
    
    # Assert: Check that participant count increased by 2
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity.replace("%20", " ")]["participants"])
    assert final_count == initial_count + 2

def test_signup_invalid_email():
    # Arrange: No setup needed
    
    # Act: Try to sign up with invalid email
    response = client.post("/activities/Chess%20Club/signup?email=invalidemail")
    
    # Assert: Check error for invalid email
    assert response.status_code == 400
    data = response.json()
    assert "Invalid email format" in data["detail"]

@pytest.mark.parametrize("invalid_email", ["", "noat"])
def test_signup_invalid_email_formats(invalid_email):
    # Arrange: No setup needed
    
    # Act: Try to sign up with various invalid emails
    response = client.post(f"/activities/Art%20Club/signup?email={invalid_email}")
    
    # Assert: Check error for invalid email
    assert response.status_code == 400
    data = response.json()
    assert "Invalid email format" in data["detail"]