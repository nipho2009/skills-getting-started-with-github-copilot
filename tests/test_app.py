from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200  # FastAPI serves static files directly
    assert response.url.path == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test structure of an activity
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test@mergington.edu for Chess Club"
    
    # Test duplicate signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()
    
    # Test nonexistent activity
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity():
    # First sign up a test user
    email = "unregistertest@mergington.edu"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Test successful unregistration
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"
    
    # Test unregistering non-registered user
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()
    
    # Test unregistering from nonexistent activity
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_max_participants():
    activity_name = "Chess Club"
    
    # Get initial activity state
    response = client.get("/activities")
    activities = response.json()
    chess_club = activities[activity_name]
    max_participants = chess_club["max_participants"]
    
    # Fill up the activity to max capacity
    current_participants = len(chess_club["participants"])
    for i in range(current_participants, max_participants):
        email = f"chess{i}@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
    
    # Try to add one more participant
    response = client.post(f"/activities/{activity_name}/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    assert "activity is full" in response.json()["detail"].lower()