"""
Unit Test Fixtures and Configuration

TESTING APPROACH:
- Provides stub interfaces for isolated unit testing
- No database or external dependencies
- Fast, lightweight test data

DESIGN PATTERNS:
1. Stub Pattern - Fake implementations of interfaces
2. Fixture Pattern - Reusable test setup
3. Test Data Builder - Sample data for common scenarios

ARCHITECTURE:
Stubs replace database layer for isolated business logic testing.
"""

import pytest
from datetime import date, timedelta


# ============================================================================
# Stub Fixtures
# ============================================================================


@pytest.fixture
def booking_stub():
    """
    Provide BookingStub instance for testing.

    RETURNS: Stub implementation of booking interface
    SCOPE: function - new instance per test
    """
    from hotel.tests.stubs.booking_stub import BookingStub

    return BookingStub()


@pytest.fixture
def room_stub():
    """
    Provide RoomStub instance for testing.

    RETURNS: Stub implementation of room interface
    SCOPE: function - new instance per test
    """
    from hotel.tests.stubs.room_stub import RoomStub

    return RoomStub()


@pytest.fixture
def customer_stub():
    """
    Provide CustomerStub instance for testing.

    RETURNS: Stub implementation of customer interface
    SCOPE: function - new instance per test
    """
    from hotel.tests.stubs.customer_stub import CustomerStub

    return CustomerStub()


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_booking_data():
    """
    Provide sample booking creation data.

    RETURNS: BookingCreateData with typical values
    USAGE: For testing booking creation operations
    """
    from hotel.operations.bookings import BookingCreateData

    return BookingCreateData(
        room_id=1,
        customer_id=1,
        from_date=date.today(),
        to_date=date.today() + timedelta(days=3),
    )


@pytest.fixture
def sample_customer_data():
    """
    Provide sample customer creation data.

    RETURNS: CustomerCreateData with typical values
    USAGE: For testing customer creation operations
    """
    from hotel.operations.customers import CustomerCreateData

    return CustomerCreateData(
        first_name="John",
        last_name="Doe",
        email_address="john.doe@example.com",
    )


@pytest.fixture
def sample_customer_update_data():
    """
    Provide sample customer update data.

    RETURNS: CustomerUpdateData with partial update values
    USAGE: For testing customer update operations
    """
    from hotel.operations.customers import CustomerUpdateData

    return CustomerUpdateData(
        first_name="Jane",
        email_address="jane.doe@example.com",
    )
