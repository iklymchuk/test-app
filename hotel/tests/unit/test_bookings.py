"""
Unit Tests for Booking Operations

TESTING APPROACH:
- Tests business logic in isolation using stub interfaces
- No database or external dependencies
- Fast execution, focused on operation layer logic
- Validates price calculations, date validations, and data flow

DESIGN PATTERNS:
1. Stub Pattern - Test doubles replace database interface
2. Arrange-Act-Assert (AAA) - Clear test structure
3. Boundary Testing - Invalid dates, edge cases
4. Exception Testing - Error handling validation

ARCHITECTURE:
Operations (business logic) → Stub Interface (fake data)

This is the LOWEST level of testing - pure unit tests.
"""

import pytest
from datetime import date
from hotel.operations.bookings import (
    read_all_bookings,
    read_booking_by_id,
    create_booking,
    delete_booking,
    BookingCreateData,
    InvalidDateError,
)
from hotel.tests.utils import assert_booking_valid, booking_sample


@pytest.mark.unit
@pytest.mark.booking
class TestBookingOperations:
    """
    Unit tests for booking operations.

    SCOPE: Business logic layer (operations/)
    PATTERN: Isolated testing with stubs
    """

    def test_read_all_bookings(self, booking_stub):
        """Verify read_all_bookings returns complete booking list."""

        result = read_all_bookings(booking_stub)

        for booking in result:
            assert_booking_valid(booking)  # Validate structure
        assert len(result) == 2

        expected_bookings = [
            booking_sample(),
            booking_sample(
                {
                    "id": 2,
                    "from_date": "2025-12-23",
                    "to_date": "2025-12-25",
                    "price": 300,
                    "customer_id": 2,
                    "room_id": 2,
                }
            ),
        ]
        for booking, expected in zip(result, expected_bookings):
            for key, value in expected.items():
                assert booking[key] == value

    def test_read_booking_by_id(self, booking_stub):
        """Verify read_booking_by_id retrieves correct booking data."""

        result = read_booking_by_id(1, booking_stub)

        assert result is not None
        assert_booking_valid(result)  # Validate structure
        expected = booking_sample()
        for key, value in expected.items():
            assert result[key] == value

    def test_create_booking_calculates_price(
        self, booking_stub, room_stub, sample_booking_data
    ):
        """Verify create_booking calculates price correctly."""

        result = create_booking(sample_booking_data, booking_stub, room_stub)

        # Assert
        assert result is not None
        assert_booking_valid(result)  # Validate structure
        assert result["id"] == 999  # Stub assigns ID 999
        assert result["price"] == 300  # 3 days * 100/day
        assert result["room_id"] == 1
        assert result["customer_id"] == 1

    def test_create_booking_invalid_dates_raises_error(self, booking_stub, room_stub):
        """Verify create_booking raises error for invalid date range."""

        # to_date before from_date (invalid!)
        booking_data = BookingCreateData(
            room_id=1,
            customer_id=1,
            from_date=date(2025, 12, 28),
            to_date=date(2025, 12, 25),  # Earlier than from_date!
        )

        with pytest.raises(InvalidDateError) as exc_info:
            create_booking(booking_data, booking_stub, room_stub)

        assert "Invalid booking dates" in str(exc_info.value)

    def test_create_booking_same_date_raises_error(self, booking_stub, room_stub):
        """Verify create_booking raises error for same-day dates."""

        booking_data = BookingCreateData(
            room_id=1,
            customer_id=1,
            from_date=date(2025, 12, 25),
            to_date=date(2025, 12, 25),  # Same day!
        )

        with pytest.raises(InvalidDateError):
            create_booking(booking_data, booking_stub, room_stub)

    def test_delete_booking(self, booking_stub):
        """Verify delete_booking removes booking successfully."""

        with pytest.raises(NotImplementedError):
            delete_booking(1, booking_stub)
