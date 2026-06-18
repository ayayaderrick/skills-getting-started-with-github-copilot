"""
Pytest tests for the Mergington High School API

Tests use Arrange-Act-Assert pattern with FastAPI TestClient
and an autouse fixture to reset global state between tests.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Module-level copy of initial activities for test isolation
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Team practices, drills, and competitive games",
        "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["noah@mergington.edu", "mia@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Swim training, technique improvement, and pool workouts",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and creative design projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "liam@mergington.edu"]
    },
    "Drama Club": {
        "description": "Practice acting, stage production, and performance skills",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["chloe@mergington.edu", "benjamin@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Study problem-solving techniques and prepare for math competitions",
        "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": ["harper@mergington.edu", "evelyn@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific topics together",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["jackson@mergington.edu", "amelia@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Autouse fixture that resets the global activities state before each test.
    Uses copy.deepcopy to ensure complete isolation between tests.
    """
    # Arrange: Reset to known initial state
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    
    yield  # Run the test
    
    # Cleanup: Reset again after test (optional, but good practice)
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Client is ready
        Act: GET /activities
        Assert: Response includes all activities with correct structure
        """
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]

    def test_get_activities_preserves_participant_lists(self, client):
        """
        Arrange: Initial state loaded
        Act: GET /activities
        Assert: Participants are correctly preserved
        """
        # Arrange (implicit via fixture)

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
        assert data["Programming Class"]["participants"] == ["emma@mergington.edu", "sophia@mergington.edu"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client):
        """
        Arrange: New email not yet signed up
        Act: POST to signup endpoint
        Assert: Student is added and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_duplicate_email_rejected(self, client):
        """
        Arrange: Email already in activity's participants
        Act: POST signup with duplicate email
        Assert: 400 error returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Activity name that doesn't exist
        Act: POST signup to nonexistent activity
        Assert: 404 error returned
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_success(self, client):
        """
        Arrange: Existing participant to remove
        Act: DELETE participant
        Assert: Student is removed and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        Arrange: Email not in activity's participants
        Act: DELETE nonexistent participant
        Assert: 404 error returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Activity that doesn't exist
        Act: DELETE participant from nonexistent activity
        Assert: 404 error returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestStateIsolation:
    """Tests verifying that state is properly isolated between tests."""

    def test_state_fresh_on_new_test(self, client):
        """
        Arrange: Beginning of isolated test
        Act: Fetch activities
        Assert: All initial participants are present (state was reset by fixture)
        """
        # Arrange (implicit via fixture reset)

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]

    def test_state_reset_after_signup(self, client):
        """
        Arrange: Fixture will reset state
        Act: Sign up a new participant (this change won't persist to next test)
        Assert: Participant is added in this test context
        """
        # Arrange
        activity = "Programming Class"
        email = "isolation_test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in activities[activity]["participants"]
