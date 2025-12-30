"""
API Integration Tests for Booking Endpoints

TESTING APPROACH:
- Tests complete booking workflow through HTTP API
- Validates integration of customer, room, and booking entities
- Tests business logic through API layer (price calculation, date validation)

DESIGN PATTERNS:
1. Composite Factory Pattern - api_booking creates dependencies
2. Full Stack Integration - No mocks, real operations and database
3. Business Rule Validation - Tests domain logic through API
4. Contract Testing - Validates API request/response contracts

ARCHITECTURE:
HTTP → Router → Operations (business logic) → DBInterface → Test DB

This is the HIGHEST level of integration testing without E2E.
"""

import pytest


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.booking
class TestBookingAPIEndpoints:
    """
    API integration tests for booking endpoints.

    SCOPE: HTTP layer + business logic + database
    PATTERN: Full stack API testing
    """

    def test_create_booking_with_valid_data(self, api_client, api_customer, api_room):
        """
        Test POST /booking creates booking successfully.

        PATTERN: Happy path integration testing
        DEMONSTRATES: Multi-entity coordination through API
        """
        # Arrange - Create dependencies
        customer = api_customer(first_name="Alice", email="alice@example.com")
        room = api_room(number="101", price=100)

        booking_data = {
            "customer_id": customer["id"],
            "room_id": room["id"],
            "from_date": "2025-12-25",
            "to_date": "2025-12-28",
        }

        # Act
        response = api_client.post("/booking", json=booking_data)

        # Assert - HTTP response
        assert response.status_code == 200

        # Assert - Response structure
        booking = response.json()
        assert "id" in booking
        assert booking["customer_id"] == customer["id"]
        assert booking["room_id"] == room["id"]
        assert booking["from_date"] == "2025-12-25"
        assert booking["to_date"] == "2025-12-28"

    def test_create_booking_calculates_price_correctly(
        self, api_client, api_customer, api_room
    ):
        """
        Test that booking price is calculated correctly.

        PATTERN: Business logic testing through API
        VALIDATES: Price calculation (3 nights * 150 = 450)
        DEMONSTRATES: Operations layer logic tested via HTTP
        """
        # Arrange
        customer = api_customer()
        room = api_room(number="201", price=150)  # 150 per night

        # Act - Book for 3 nights
        response = api_client.post(
            "/booking",
            json={
                "customer_id": customer["id"],
                "room_id": room["id"],
                "from_date": "2025-12-20",
                "to_date": "2025-12-23",  # 3 nights
            },
        )

        # Assert - Price calculated correctly
        assert response.status_code == 200
        assert response.json()["price"] == 450  # 3 * 150

    def test_read_all_bookings_returns_empty_list_initially(self, api_client):
        """
        Test GET /bookings with no data.

        PATTERN: Empty state testing
        """
        # Act
        response = api_client.get("/bookings")

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_read_all_bookings_returns_created_bookings(self, api_client, api_booking):
        """
        Test GET /bookings returns all bookings.

        PATTERN: List endpoint testing with factory
        """
        # Arrange - Create multiple bookings
        booking1 = api_booking(from_date="2025-12-01", to_date="2025-12-05")
        booking2 = api_booking(from_date="2025-12-10", to_date="2025-12-15")

        # Act
        response = api_client.get("/bookings")

        # Assert
        assert response.status_code == 200
        bookings = response.json()
        assert len(bookings) == 2

        booking_ids = [b["id"] for b in bookings]
        assert booking1["id"] in booking_ids
        assert booking2["id"] in booking_ids

    def test_read_booking_by_id_returns_correct_booking(self, api_client, api_booking):
        """
        Test GET /booking/{id} returns specific booking.

        PATTERN: Detail endpoint testing
        """
        # Arrange
        created = api_booking(from_date="2025-12-25", to_date="2025-12-28")
        booking_id = created["id"]

        # Act
        response = api_client.get(f"/booking/{booking_id}")

        # Assert
        assert response.status_code == 200
        booking = response.json()
        assert booking["id"] == booking_id
        assert booking["from_date"] == "2025-12-25"
        assert booking["to_date"] == "2025-12-28"

    def test_delete_booking_removes_booking(self, api_client, api_booking):
        """
        Test DELETE /booking/{id} removes booking.

        PATTERN: Delete endpoint testing
        """
        # Arrange - Create booking
        created = api_booking()
        booking_id = created["id"]

        # Act - Delete
        delete_response = api_client.delete(f"/booking/{booking_id}")

        # Assert - Deletion successful
        assert delete_response.status_code == 200

        # Assert - Booking no longer in list
        list_response = api_client.get("/bookings")
        booking_ids = [b["id"] for b in list_response.json()]
        assert booking_id not in booking_ids


@pytest.mark.api
@pytest.mark.integration
class TestBookingAPIBusinessLogic:
    """
    Business logic validation through API layer.

    SCOPE: Domain rules enforced via HTTP
    DEMONSTRATES: Testing business logic without direct unit tests
    """

    def test_booking_price_varies_with_room_price(
        self, api_client, api_customer, api_room
    ):
        """
        Test that different room prices affect booking price.

        PATTERN: Business rule validation via API
        """
        # Arrange
        customer = api_customer()
        cheap_room = api_room(number="CHEAP", price=50)
        expensive_room = api_room(number="EXPENSIVE", price=300)

        # Act - Book same duration, different rooms
        cheap_booking_response = api_client.post(
            "/booking",
            json={
                "customer_id": customer["id"],
                "room_id": cheap_room["id"],
                "from_date": "2025-12-01",
                "to_date": "2025-12-04",  # 3 nights
            },
        )

        expensive_booking_response = api_client.post(
            "/booking",
            json={
                "customer_id": customer["id"],
                "room_id": expensive_room["id"],
                "from_date": "2025-12-10",
                "to_date": "2025-12-13",  # 3 nights
            },
        )

        # Assert - Prices different based on room
        cheap_price = cheap_booking_response.json()["price"]
        expensive_price = expensive_booking_response.json()["price"]

        assert cheap_price == 150  # 3 * 50
        assert expensive_price == 900  # 3 * 300
        assert expensive_price > cheap_price

    def test_booking_price_varies_with_duration(
        self, api_client, api_customer, api_room
    ):
        """
        Test that booking duration affects price.

        PATTERN: Business rule validation
        """
        # Arrange
        customer = api_customer()
        room = api_room(number="STD", price=100)

        # Act - Book different durations
        short_stay = api_client.post(
            "/booking",
            json={
                "customer_id": customer["id"],
                "room_id": room["id"],
                "from_date": "2025-12-01",
                "to_date": "2025-12-03",  # 2 nights
            },
        )

        long_stay = api_client.post(
            "/booking",
            json={
                "customer_id": customer["id"],
                "room_id": room["id"],
                "from_date": "2025-12-10",
                "to_date": "2025-12-15",  # 5 nights
            },
        )

        # Assert
        assert short_stay.json()["price"] == 200  # 2 * 100
        assert long_stay.json()["price"] == 500  # 5 * 100


@pytest.mark.api
@pytest.mark.integration
class TestBookingAPIWorkflows:
    """
    Complete booking workflows through API.

    SCOPE: Multi-step business processes
    DEMONSTRATES: Real-world usage patterns
    """

    def test_complete_booking_workflow(self, api_client):
        """
        Test complete workflow: create customer → room → booking → read.

        PATTERN: End-to-end workflow testing
        DEMONSTRATES: Multi-entity coordination
        """
        # Step 1: Create customer
        customer_response = api_client.post(
            "/customer",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email_address": "john.doe@example.com",
            },
        )
        assert customer_response.status_code == 200
        customer_id = customer_response.json()["id"]

        # Step 2: Create room
        room_response = api_client.post(
            "/room", json={"number": "WORKFLOW", "size": 30, "price": 120}
        )
        assert room_response.status_code == 200
        room_id = room_response.json()["id"]

        # Step 3: Create booking
        booking_response = api_client.post(
            "/booking",
            json={
                "customer_id": customer_id,
                "room_id": room_id,
                "from_date": "2025-12-25",
                "to_date": "2025-12-30",  # 5 nights
            },
        )
        assert booking_response.status_code == 200
        booking = booking_response.json()
        assert booking["price"] == 600  # 5 * 120

        # Step 4: Read booking back
        read_response = api_client.get(f"/booking/{booking['id']}")
        assert read_response.status_code == 200
        assert read_response.json()["customer_id"] == customer_id
        assert read_response.json()["room_id"] == room_id

    def test_multiple_bookings_for_same_customer(
        self, api_client, api_customer, api_room
    ):
        """
        Test customer can have multiple bookings.

        PATTERN: One-to-many relationship testing
        """
        # Arrange
        customer = api_customer(first_name="Frequent", last_name="Guest")
        room1 = api_room(number="R1")
        room2 = api_room(number="R2")

        # Act - Create multiple bookings for same customer
        booking1 = api_client.post(
            "/booking",
            json={
                "customer_id": customer["id"],
                "room_id": room1["id"],
                "from_date": "2025-12-01",
                "to_date": "2025-12-05",
            },
        )

        booking2 = api_client.post(
            "/booking",
            json={
                "customer_id": customer["id"],
                "room_id": room2["id"],
                "from_date": "2025-12-10",
                "to_date": "2025-12-15",
            },
        )

        # Assert - Both created
        assert booking1.status_code == 200
        assert booking2.status_code == 200

        # Assert - Both for same customer
        all_bookings = api_client.get("/bookings").json()
        customer_bookings = [
            b for b in all_bookings if b["customer_id"] == customer["id"]
        ]
        assert len(customer_bookings) == 2

    def test_create_read_delete_workflow(self, api_client, api_booking):
        """
        Test create → read → delete workflow.

        PATTERN: CRUD workflow testing
        """
        # Create
        created = api_booking()
        booking_id = created["id"]

        # Read
        read_response = api_client.get(f"/booking/{booking_id}")
        assert read_response.status_code == 200
        assert read_response.json()["id"] == booking_id

        # Delete
        delete_response = api_client.delete(f"/booking/{booking_id}")
        assert delete_response.status_code == 200

        # Verify deleted
        all_bookings = api_client.get("/bookings").json()
        assert booking_id not in [b["id"] for b in all_bookings]
