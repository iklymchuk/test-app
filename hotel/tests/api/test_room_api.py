"""
API Integration Tests for Room Endpoints

TESTING APPROACH:
- Hits real FastAPI app using TestClient
- No stubs/mocks: exercises routers → operations → DBInterface → SQLite
- Validates status codes, payload schemas, and JSON serialization

DESIGN PATTERNS:
1. Full Stack Integration - Verifies entire HTTP stack per request
2. Arrange-Act-Assert - Consistent test narrative
3. Factory Pattern - `api_room` fixture provisions data via HTTP
4. Contract Testing - Ensures response bodies follow schema expectations

ARCHITECTURE:
HTTP Request → FastAPI Router → Operations Module → DBInterface → Test DB
"""

import pytest


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.room
class TestRoomAPIEndpoints:
    """
    API integration tests for room endpoints.

    PATTERN: RESTful API testing
    SCOPE: HTTP layer + full application stack
    """

    def test_read_all_rooms_empty_initially(self, api_client):
        """
        Test GET /rooms returns empty list with no data.

        PATTERN: Initial state testing
        """
        # Act
        response = api_client.get("/rooms")

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_read_all_rooms_returns_created_rooms(self, api_client, api_room):
        """
        Test GET /rooms returns all rooms.

        PATTERN: List endpoint testing
        """
        # Arrange - Create rooms via API factory
        room1 = api_room(number="101", size=25, price=100)
        room2 = api_room(number="102", size=30, price=150)

        # Act
        response = api_client.get("/rooms")

        # Assert
        assert response.status_code == 200
        rooms = response.json()
        assert len(rooms) == 2

        room_numbers = [r["number"] for r in rooms]
        assert "101" in room_numbers
        assert "102" in room_numbers

    def test_read_room_by_id_returns_correct_room(self, api_client, api_room):
        """
        Test GET /room/{id} returns specific room.

        PATTERN: Detail endpoint testing
        """
        # Arrange
        created = api_room(number="201", size=40, price=200)
        room_id = created["id"]

        # Act
        response = api_client.get(f"/room/{room_id}")

        # Assert
        assert response.status_code == 200
        room = response.json()
        assert room["id"] == room_id
        assert room["number"] == "201"
        assert room["size"] == 40
        assert room["price"] == 200


@pytest.mark.api
@pytest.mark.integration
class TestRoomAPIScenarios:
    """
    Real-world room management scenarios.

    DEMONSTRATES: Business workflows through API
    """

    def test_query_rooms_by_characteristics(self, api_client, api_room):
        """
        Test creating rooms with different characteristics.

        PATTERN: Data variety testing
        NOTE: Current API doesn't have filtering, but tests data creation
        """
        # Arrange - Create variety of rooms
        small_cheap = api_room(number="SMALL", size=15, price=50)
        medium = api_room(number="MED", size=25, price=100)
        large_expensive = api_room(number="SUITE", size=50, price=300)

        # Act - Read all
        response = api_client.get("/rooms")

        # Assert - All rooms present
        assert response.status_code == 200
        rooms = response.json()
        assert len(rooms) == 3

        # Verify variety
        prices = [r["price"] for r in rooms]
        assert min(prices) == 50
        assert max(prices) == 300

    def test_rooms_persist_across_multiple_reads(self, api_client, api_room):
        """
        Test room data persists across multiple API calls.

        PATTERN: Persistence verification
        """
        # Arrange - Create room
        created = api_room(number="PERSIST", size=30, price=120)
        room_id = created["id"]

        # Act - Read multiple times
        response1 = api_client.get(f"/room/{room_id}")
        response2 = api_client.get(f"/room/{room_id}")
        response3 = api_client.get(f"/room/{room_id}")

        # Assert - All reads return same data
        assert response1.json() == response2.json() == response3.json()
        assert response1.json()["number"] == "PERSIST"

    def test_alphanumeric_room_numbers_supported(self, api_client, api_room):
        """
        Test that room numbers can be alphanumeric.

        PATTERN: Input format testing
        """
        # Arrange & Act
        room_a = api_room(number="A101")
        room_b = api_room(number="PENT-01")
        room_c = api_room(number="999")

        # Assert - All created successfully
        assert room_a["number"] == "A101"
        assert room_b["number"] == "PENT-01"
        assert room_c["number"] == "999"

        # Assert - All retrievable
        response = api_client.get("/rooms")
        room_numbers = [r["number"] for r in response.json()]
        assert "A101" in room_numbers
        assert "PENT-01" in room_numbers
        assert "999" in room_numbers
