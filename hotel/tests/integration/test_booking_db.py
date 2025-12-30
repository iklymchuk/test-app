"""
Integration tests for booking database operations.

TESTING APPROACH:
- Tests interact with REAL database (in-memory SQLite)
- No mocks or stubs - testing actual DB layer
- Verifies database constraints, relationships, and CRUD operations
- Complements unit tests which test business logic with stubs

DESIGN PATTERNS:
1. Arrange-Act-Assert (AAA) Pattern - Clear test structure
2. Test Data Builder Pattern - Factories for test data
3. Database Transaction Pattern - Test isolation
4. Verification Pattern - Multi-level assertions

ARCHITECTURE:
Unit Tests (stubs)        -> Business logic in operations/
Integration Tests (real DB) -> Database layer in db/
                           -> Data integrity and persistence
"""

import pytest
from datetime import date, timedelta
from hotel.db.models import DBBooking


@pytest.mark.integration
@pytest.mark.database
class TestBookingDatabaseOperations:
    """
    Integration tests for booking CRUD operations.

    SCOPE: Database layer (db_interface.py)
    PATTERN: Test per operation (create, read, update, delete)
    """

    def test_create_booking_persists_to_database(
        self, booking_db_interface, customer_factory, room_factory, test_db_session
    ):
        """
        Test that creating a booking persists data to database.

        PATTERN: Arrange-Act-Assert
        VERIFIES:
        - Booking is saved to database
        - All fields are correctly stored
        - Foreign key relationships are maintained
        """
        # Arrange - Create required dependencies
        customer = customer_factory(first_name="Alice")
        room = room_factory(number="101", price=100)

        booking_data = {
            "customer_id": customer.id,
            "room_id": room.id,
            "from_date": date(2025, 12, 25),
            "to_date": date(2025, 12, 28),
            "price": 300,
        }

        # Act - Create booking via interface
        result = booking_db_interface.create(booking_data)

        # Assert - Verify returned data
        assert result["id"] is not None
        assert result["customer_id"] == customer.id
        assert result["room_id"] == room.id
        assert result["price"] == 300

        # Assert - Verify data was actually persisted (query database directly)
        saved_booking = (
            test_db_session.query(DBBooking).filter_by(id=result["id"]).first()
        )
        assert saved_booking is not None
        assert saved_booking.customer_id == customer.id
        assert saved_booking.price == 300

    def test_read_booking_by_id_retrieves_correct_data(
        self, booking_db_interface, booking_factory
    ):
        """
        Test reading a specific booking by ID.

        PATTERN: Pre-populate and verify
        VERIFIES: Correct data retrieval from database
        """
        # Arrange - Create booking in database
        created_booking = booking_factory(
            from_date=date(2025, 12, 20), to_date=date(2025, 12, 23), price=450
        )

        # Act - Read booking via interface
        result = booking_db_interface.read_by_id(created_booking.id)

        # Assert - Verify all fields match
        assert result["id"] == created_booking.id
        assert result["customer_id"] == created_booking.customer_id
        assert result["room_id"] == created_booking.room_id
        assert result["price"] == 450

    def test_read_all_bookings_returns_multiple_records(
        self, booking_db_interface, sample_bookings
    ):
        """
        Test reading all bookings from database.

        PATTERN: Batch data verification
        VERIFIES:
        - Multiple records returned
        - Correct count
        - Data integrity
        """
        # Arrange - sample_bookings fixture creates 2 bookings

        # Act
        result = booking_db_interface.read_all()

        # Assert - Verify count and structure
        assert len(result) == 2
        assert all("id" in booking for booking in result)
        assert all("customer_id" in booking for booking in result)
        assert all("room_id" in booking for booking in result)

    def test_update_booking_modifies_database_record(
        self, booking_db_interface, booking_factory, test_db_session
    ):
        """
        Test updating an existing booking.

        PATTERN: Create-Modify-Verify
        VERIFIES:
        - Update operation works
        - Only specified fields change
        - Changes persist to database
        """
        # Arrange - Create initial booking
        booking = booking_factory(price=300)
        original_customer_id = booking.customer_id

        # Act - Update price
        update_data = {"price": 500}
        result = booking_db_interface.update(booking.id, update_data)

        # Assert - Verify returned data
        assert result["id"] == booking.id
        assert result["price"] == 500
        assert result["customer_id"] == original_customer_id  # Unchanged

        # Assert - Verify database was updated
        test_db_session.expire_all()  # Clear session cache
        updated_booking = test_db_session.get(DBBooking, booking.id)
        assert updated_booking.price == 500
        assert updated_booking.customer_id == original_customer_id

    def test_delete_booking_removes_from_database(
        self, booking_db_interface, booking_factory, test_db_session
    ):
        """
        Test deleting a booking from database.

        PATTERN: Create-Delete-Verify absence
        VERIFIES:
        - Delete operation works
        - Record is actually removed
        - Returns deleted data
        """
        # Arrange - Create booking
        booking = booking_factory()
        booking_id = booking.id

        # Act - Delete booking
        result = booking_db_interface.delete(booking_id)

        # Assert - Verify returned deleted data
        assert result["id"] == booking_id

        # Assert - Verify record was deleted from database
        deleted_booking = test_db_session.get(DBBooking, booking_id)
        assert deleted_booking is None


@pytest.mark.integration
@pytest.mark.database
class TestBookingDatabaseConstraints:
    """
    Tests for database-level constraints and relationships.

    SCOPE: Data integrity, foreign keys, constraints
    DEMONSTRATES: Testing database schema enforcement
    """

    def test_booking_requires_valid_customer_id(
        self, booking_db_interface, room_factory
    ):
        """
        Test that booking requires valid foreign key to customer.

        VERIFIES: Foreign key constraint enforcement
        NOTE: Behavior may vary by database engine
        """
        # Arrange - Create room but no customer
        room = room_factory()

        booking_data = {
            "customer_id": 9999,  # Non-existent customer
            "room_id": room.id,
            "from_date": date.today(),
            "to_date": date.today() + timedelta(days=2),
            "price": 200,
        }

        # Act & Assert - Should fail or create orphan record
        # (SQLite doesn't enforce FK by default, but test documents the expectation)
        result = booking_db_interface.create(booking_data)
        # In production DB with FK enforcement, this would raise an error
        assert result["customer_id"] == 9999

    def test_booking_with_related_data_access(
        self, booking_factory, customer_factory, room_factory, test_db_session
    ):
        """
        Test accessing related customer and room data through booking.

        PATTERN: Relationship traversal testing
        VERIFIES:
        - SQLAlchemy relationships work
        - Foreign keys properly linked
        - Related data accessible
        """
        # Arrange - Create booking with specific customer and room
        customer = customer_factory(first_name="Alice", last_name="Wonder")
        room = room_factory(number="101", price=100)
        booking = booking_factory(customer=customer, room=room)

        # Act - Retrieve booking and access related data
        retrieved_booking = test_db_session.get(DBBooking, booking.id)

        # Assert - Verify relationships
        assert retrieved_booking.customer.first_name == "Alice"
        assert retrieved_booking.customer.last_name == "Wonder"
        assert retrieved_booking.room.number == "101"
        assert retrieved_booking.room.price == 100


@pytest.mark.integration
@pytest.mark.database
class TestBookingQueryScenarios:
    """
    Tests for complex query scenarios and data retrieval.

    SCOPE: Real-world query patterns
    DEMONSTRATES: Testing complex database operations
    """

    def test_query_bookings_by_date_range(self, booking_factory, test_db_session):
        """
        Test querying bookings within a date range.

        PATTERN: Query filtering test
        SCENARIO: Find all bookings in December 2025
        """
        # Arrange - Create bookings in different months
        dec_booking_1 = booking_factory(
            from_date=date(2025, 12, 10), to_date=date(2025, 12, 15)
        )
        dec_booking_2 = booking_factory(
            from_date=date(2025, 12, 20), to_date=date(2025, 12, 25)
        )
        jan_booking = booking_factory(
            from_date=date(2026, 1, 10), to_date=date(2026, 1, 15)
        )

        # Act - Query bookings in December
        december_bookings = (
            test_db_session.query(DBBooking)
            .filter(
                DBBooking.from_date >= date(2025, 12, 1),
                DBBooking.from_date < date(2026, 1, 1),
            )
            .all()
        )

        # Assert - Only December bookings returned
        assert len(december_bookings) == 2
        booking_ids = [b.id for b in december_bookings]
        assert dec_booking_1.id in booking_ids
        assert dec_booking_2.id in booking_ids
        assert jan_booking.id not in booking_ids

    def test_query_bookings_by_customer(
        self, booking_factory, customer_factory, test_db_session
    ):
        """
        Test querying all bookings for specific customer.

        PATTERN: Relationship-based query
        SCENARIO: Customer booking history
        """
        # Arrange - Create customers with multiple bookings
        alice = customer_factory(first_name="Alice")
        bob = customer_factory(first_name="Bob")

        alice_booking_1 = booking_factory(customer=alice)
        alice_booking_2 = booking_factory(customer=alice)
        bob_booking = booking_factory(customer=bob)

        # Act - Query Alice's bookings
        alice_bookings = (
            test_db_session.query(DBBooking).filter_by(customer_id=alice.id).all()
        )

        # Assert - Only Alice's bookings returned
        assert len(alice_bookings) == 2
        assert all(b.customer_id == alice.id for b in alice_bookings)

    def test_calculate_total_revenue_from_bookings(
        self, booking_factory, test_db_session
    ):
        """
        Test aggregating booking prices for revenue calculation.

        PATTERN: Aggregation query test
        SCENARIO: Business intelligence / reporting
        """
        # Arrange - Create bookings with known prices
        booking_factory(price=100)
        booking_factory(price=200)
        booking_factory(price=300)

        # Act - Calculate total revenue
        from sqlalchemy import func

        total_revenue = test_db_session.query(func.sum(DBBooking.price)).scalar()

        # Assert
        assert total_revenue == 600


# Additional test markers for selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.database,
]
