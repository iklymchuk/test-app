"""
Integration tests for room database operations.

TESTING PHILOSOPHY:
- Integration tests verify database layer works correctly
- Unit tests (with stubs) verify business logic
- Different concerns, different test types

PATTERNS SHOWCASED:
1. State-based Testing - Verify database state changes
2. Property-based Testing - Test data properties and constraints
3. Boundary Testing - Edge cases for room attributes
4. Relationship Testing - Room-booking associations
"""

import pytest
from sqlalchemy import func
from hotel.db.models import DBRoom, DBBooking


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.room
class TestRoomDatabaseOperations:
    """
    Integration tests for room CRUD operations.

    SCOPE: Database persistence layer
    STRATEGY: Test actual database operations, not business logic
    """

    def test_create_room_with_all_attributes(
        self, room_db_interface, test_db_session, db_query_helper
    ):
        """
        Test creating a room with complete data.

        PATTERN: Complete attribute verification
        """
        # Arrange
        initial_count = db_query_helper.count_rooms()

        room_data = {"number": "101", "size": 25, "price": 150}

        # Act
        result = room_db_interface.create(room_data)

        # Assert - Returned data structure
        assert result["id"] is not None
        assert result["number"] == "101"
        assert result["size"] == 25
        assert result["price"] == 150

        # Assert - Database persistence
        assert db_query_helper.count_rooms() == initial_count + 1

        # Assert - Direct database query
        saved_room = test_db_session.get(DBRoom, result["id"])
        assert saved_room.number == "101"
        assert saved_room.size == 25
        assert saved_room.price == 150

    def test_read_room_by_id_retrieves_exact_match(
        self, room_db_interface, room_factory
    ):
        """
        Test reading specific room by ID.

        PATTERN: Identity-based retrieval
        """
        # Arrange
        created = room_factory(number="202", size=30, price=200)

        # Act
        result = room_db_interface.read_by_id(created.id)

        # Assert
        assert result["id"] == created.id
        assert result["number"] == "202"
        assert result["size"] == 30
        assert result["price"] == 200

    def test_read_all_rooms_returns_complete_inventory(
        self, room_db_interface, sample_rooms
    ):
        """
        Test retrieving all rooms from database.

        PATTERN: Complete collection retrieval
        USES: Pre-populated fixture with 3 rooms
        """
        # Arrange - sample_rooms creates: 101, 201, 301

        # Act
        result = room_db_interface.read_all()

        # Assert - Collection properties
        assert len(result) == 3
        assert all("id" in room for room in result)
        assert all("number" in room for room in result)
        assert all("size" in room for room in result)
        assert all("price" in room for room in result)

        # Assert - Specific room numbers present
        room_numbers = [r["number"] for r in result]
        assert "101" in room_numbers
        assert "201" in room_numbers
        assert "301" in room_numbers

    def test_update_room_price_preserves_other_fields(
        self, room_db_interface, room_factory, test_db_session
    ):
        """
        Test updating room price without affecting other attributes.

        PATTERN: Selective field update
        VERIFIES: Immutability of non-updated fields
        """
        # Arrange
        room = room_factory(number="301", size=40, price=250)
        original_id = room.id

        # Act - Update only price
        update_data = {"price": 300}
        result = room_db_interface.update(room.id, update_data)

        # Assert - Price changed
        assert result["price"] == 300

        # Assert - Other fields unchanged
        assert result["id"] == original_id
        assert result["number"] == "301"
        assert result["size"] == 40

        # Assert - Database reflects change
        test_db_session.expire_all()
        updated_room = test_db_session.get(DBRoom, original_id)
        assert updated_room.price == 300
        assert updated_room.number == "301"

    def test_delete_room_removes_from_inventory(
        self, room_db_interface, room_factory, test_db_session, db_query_helper
    ):
        """
        Test room deletion from database.

        PATTERN: Remove and verify absence
        """
        # Arrange
        room = room_factory(number="999")
        room_id = room.id
        initial_count = db_query_helper.count_rooms()

        # Act
        result = room_db_interface.delete(room_id)

        # Assert - Returns deleted room data
        assert result["id"] == room_id
        assert result["number"] == "999"

        # Assert - Room removed from database
        assert db_query_helper.count_rooms() == initial_count - 1
        deleted_room = test_db_session.get(DBRoom, room_id)
        assert deleted_room is None


@pytest.mark.integration
@pytest.mark.database
class TestRoomDataValidation:
    """
    Tests for room data constraints and edge cases.

    DEMONSTRATES: Boundary testing and data validation
    """

    @pytest.mark.parametrize(
        "size,price",
        [
            (1, 1),  # Minimum values
            (10, 50),  # Small room, budget price
            (50, 500),  # Large room, premium price
            (100, 1000),  # Suite, luxury price
            (200, 5000),  # Penthouse extreme
        ],
    )
    def test_create_rooms_with_various_sizes_and_prices(
        self, room_db_interface, size, price
    ):
        """
        Test room creation with different size/price combinations.

        PATTERN: Parametrized boundary testing
        DEMONSTRATES: Testing valid range of values
        """
        # Arrange
        room_data = {"number": f"R{size}", "size": size, "price": price}

        # Act
        result = room_db_interface.create(room_data)

        # Assert
        assert result["size"] == size
        assert result["price"] == price

    def test_room_numbers_can_be_alphanumeric(self, room_factory):
        """
        Test that room numbers support various formats.

        PATTERN: Format validation
        SCENARIO: Different room numbering schemes
        """
        # Arrange & Act
        numeric_room = room_factory(number="101")
        alpha_room = room_factory(number="A-101")
        suite_room = room_factory(number="SUITE-1")

        # Assert
        assert numeric_room.number == "101"
        assert alpha_room.number == "A-101"
        assert suite_room.number == "SUITE-1"

    def test_rooms_have_unique_ids(self, room_factory):
        """
        Test that each room gets unique auto-incremented ID.

        PATTERN: Primary key uniqueness verification
        """
        # Arrange & Act
        room1 = room_factory()
        room2 = room_factory()
        room3 = room_factory()

        # Assert - All IDs unique
        ids = {room1.id, room2.id, room3.id}
        assert len(ids) == 3

        # Assert - Sequential (auto-increment)
        assert room1.id < room2.id < room3.id


@pytest.mark.integration
@pytest.mark.database
class TestRoomQueryScenarios:
    """
    Tests for room search and filtering operations.

    DEMONSTRATES: Complex query patterns
    """

    def test_find_room_by_number(self, room_factory, db_query_helper):
        """
        Test searching room by room number.

        PATTERN: Unique identifier search
        SCENARIO: Room lookup by number
        """
        # Arrange
        room_factory(number="101")
        room_factory(number="102")
        room_factory(number="201")

        # Act
        found = db_query_helper.get_room_by_number("102")

        # Assert
        assert found is not None
        assert found.number == "102"

    def test_find_rooms_within_price_range(self, room_factory, test_db_session):
        """
        Test querying rooms by price range.

        PATTERN: Range query testing
        SCENARIO: Budget-based room search
        """
        # Arrange - Create rooms with various prices
        room_factory(number="101", price=100)  # Budget
        room_factory(number="201", price=150)  # Mid-range
        room_factory(number="301", price=200)  # Mid-range
        room_factory(number="401", price=300)  # Premium

        # Act - Find mid-range rooms ($125-$225)
        mid_range = (
            test_db_session.query(DBRoom)
            .filter(DBRoom.price >= 125, DBRoom.price <= 225)
            .all()
        )

        # Assert
        assert len(mid_range) == 2
        prices = [r.price for r in mid_range]
        assert 150 in prices
        assert 200 in prices

    def test_find_rooms_by_minimum_size(self, room_factory, test_db_session):
        """
        Test finding rooms above minimum size.

        PATTERN: Threshold filtering
        SCENARIO: Size-based room filtering
        """
        # Arrange
        room_factory(number="S1", size=15)  # Small
        room_factory(number="M1", size=25)  # Medium
        room_factory(number="L1", size=40)  # Large
        room_factory(number="L2", size=50)  # Large

        # Act - Find rooms >= 30 sq meters
        large_rooms = test_db_session.query(DBRoom).filter(DBRoom.size >= 30).all()

        # Assert
        assert len(large_rooms) == 2
        assert all(r.size >= 30 for r in large_rooms)

    def test_calculate_average_room_price(self, room_factory, test_db_session):
        """
        Test aggregating room prices for statistics.

        PATTERN: Aggregation query
        SCENARIO: Price analytics
        """
        # Arrange
        room_factory(price=100)
        room_factory(price=200)
        room_factory(price=300)

        # Act
        avg_price = test_db_session.query(func.avg(DBRoom.price)).scalar()

        # Assert
        assert avg_price == 200.0


@pytest.mark.integration
@pytest.mark.database
class TestRoomAvailability:
    """
    Tests for room availability and booking relationships.

    DEMONSTRATES: Complex relationship queries
    """

    def test_room_with_multiple_bookings(
        self, room_factory, booking_factory, test_db_session
    ):
        """
        Test room can have multiple bookings.

        PATTERN: One-to-many relationship verification
        SCENARIO: Popular room booking history
        """
        # Arrange
        popular_room = room_factory(number="SUITE-1")

        booking_factory(room=popular_room)
        booking_factory(room=popular_room)
        booking_factory(room=popular_room)

        # Act - Query room's bookings
        room_bookings = (
            test_db_session.query(DBBooking).filter_by(room_id=popular_room.id).all()
        )

        # Assert
        assert len(room_bookings) == 3
        assert all(b.room_id == popular_room.id for b in room_bookings)

    def test_find_rooms_without_bookings(
        self, room_factory, booking_factory, test_db_session
    ):
        """
        Test finding available rooms (no bookings).

        PATTERN: Left join query for unmatched records
        SCENARIO: Find vacant rooms
        """
        # Arrange
        booked_room = room_factory(number="101")
        vacant_room_1 = room_factory(number="201")
        vacant_room_2 = room_factory(number="301")

        booking_factory(room=booked_room)

        # Act - Find rooms without bookings

        vacant_rooms = (
            test_db_session.query(DBRoom)
            .outerjoin(DBBooking, DBRoom.id == DBBooking.room_id)
            .filter(DBBooking.id.is_(None))
            .all()
        )

        # Assert
        assert len(vacant_rooms) == 2
        vacant_numbers = [r.number for r in vacant_rooms]
        assert "201" in vacant_numbers
        assert "301" in vacant_numbers
        assert "101" not in vacant_numbers

    def test_delete_room_with_existing_bookings(
        self, room_db_interface, room_factory, booking_factory, test_db_session
    ):
        """
        Test deleting room that has bookings.

        PATTERN: Referential integrity testing
        NOTE: Documents current behavior - production might prevent this
        """
        # Arrange
        room = room_factory(number="TEMP")
        room_id = room.id

        # Act - Delete room
        room_db_interface.delete(room_id)

        # Assert - Room deleted
        deleted_room = test_db_session.get(DBRoom, room_id)
        assert deleted_room is None

        # Note: Booking becomes orphaned
        # Production system might use CASCADE or prevent deletion


@pytest.mark.integration
@pytest.mark.database
class TestRoomBusinessRules:
    """
    Tests for business rules related to rooms.

    DEMONSTRATES: Testing domain logic at integration level
    """

    def test_premium_rooms_cost_more_than_standard(self, room_factory, test_db_session):
        """
        Test business rule: Larger rooms should cost more.

        PATTERN: Business rule verification
        """
        # Arrange
        standard = room_factory(size=20, price=100)
        deluxe = room_factory(size=30, price=150)
        suite = room_factory(size=50, price=250)

        # Assert - Price increases with size
        assert standard.price < deluxe.price < suite.price
        assert standard.size < deluxe.size < suite.size

    def test_query_rooms_ordered_by_price(self, room_factory, test_db_session):
        """
        Test sorting rooms by price.

        PATTERN: Ordering verification
        SCENARIO: Show rooms from cheapest to most expensive
        """
        # Arrange - Create rooms in random price order
        room_factory(price=200)
        room_factory(price=100)
        room_factory(price=300)
        room_factory(price=150)

        # Act - Query ordered by price
        rooms_by_price = test_db_session.query(DBRoom).order_by(DBRoom.price).all()

        # Assert - Ascending order
        prices = [r.price for r in rooms_by_price]
        assert prices == sorted(prices)
        assert prices == [100, 150, 200, 300]
