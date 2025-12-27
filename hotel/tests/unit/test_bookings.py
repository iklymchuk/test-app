"""
Unit tests for booking operations using BookingStubInterface.
Testing business logic with inheritance-based stubs.
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
from hotel.tests.utils import assert_booking_valid


@pytest.mark.unit
@pytest.mark.booking
class TestBookingOperations:
    """Test booking operations with stub data."""

    def test_read_all_bookings(self, booking_stub):
        """Test reading all bookings returns stubbed data."""

        result = read_all_bookings(booking_stub)

        for booking in result:
            assert_booking_valid(booking)  # Validate structure
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["price"] == 200
        assert result[1]["id"] == 2
        assert result[1]["price"] == 300

    def test_read_booking_by_id(self, booking_stub):
        """Test reading a specific booking by ID."""

        result = read_booking_by_id(1, booking_stub)

        assert result is not None
        assert_booking_valid(result)  # Validate structure
        assert result["from_date"] == "2025-12-24"
        assert result["to_date"] == "2025-12-26"
        assert result["price"] == 200
        assert result["customer_id"] == 1
        assert result["room_id"] == 1

    def test_create_booking_calculates_price(
        self, booking_stub, room_stub, sample_booking_data
    ):
        """Test that booking creation calculates price correctly."""

        result = create_booking(sample_booking_data, booking_stub, room_stub)

        # Assert
        assert result is not None
        assert_booking_valid(result)  # Validate structure
        assert result["id"] == 999  # Stub assigns ID 999
        assert result["price"] == 300  # 3 days * 100/day
        assert result["room_id"] == 1
        assert result["customer_id"] == 1

    def test_create_booking_invalid_dates_raises_error(self, booking_stub, room_stub):
        """Test that invalid dates raise InvalidDateError."""

        # to_date before from_date (invalid!)
        booking_data = BookingCreateData(
            room_id=1,
            customer_id=1,
            from_date=date(2025, 12, 28),
            to_date=date(2025, 12, 25),  # Earlier than from_date!
        )

        # Act & Assert
        with pytest.raises(InvalidDateError) as exc_info:
            create_booking(booking_data, booking_stub, room_stub)

        assert "Invalid booking dates" in str(exc_info.value)

    def test_create_booking_same_date_raises_error(self, booking_stub, room_stub):
        """Test that same from_date and to_date raises error."""

        booking_data = BookingCreateData(
            room_id=1,
            customer_id=1,
            from_date=date(2025, 12, 25),
            to_date=date(2025, 12, 25),  # Same day!
        )

        # Act & Assert
        with pytest.raises(InvalidDateError):
            create_booking(booking_data, booking_stub, room_stub)

    def test_delete_booking(self, booking_stub):
        """Test deleting a booking."""

        with pytest.raises(NotImplementedError):
            delete_booking(1, booking_stub)
