"""
This file contains shared fixtures and configuration for unit tests.
"""

import pytest
from datetime import date, timedelta


# ============================================================================
# Stub Fixtures - Reusable test doubles
# ============================================================================


@pytest.fixture
def booking_stub():
    """Provide a BookingStub instance for tests."""
    from hotel.tests.stubs.booking_stub import BookingStub

    return BookingStub()


@pytest.fixture
def room_stub():
    """Provide a RoomStub instance for tests."""
    from hotel.tests.stubs.room_stub import RoomStub

    return RoomStub()


@pytest.fixture
def customer_stub():
    """Provide a CustomerStub instance for tests."""
    from hotel.tests.stubs.customer_stub import CustomerStub

    return CustomerStub()


# ============================================================================
# Data Fixtures - Test data builders
# ============================================================================


@pytest.fixture
def sample_booking_data():
    """Provide sample booking creation data."""
    from hotel.operations.bookings import BookingCreateData

    return BookingCreateData(
        room_id=1,
        customer_id=1,
        from_date=date.today(),
        to_date=date.today() + timedelta(days=3),
    )


@pytest.fixture
def sample_customer_data():
    """Provide sample customer creation data."""
    from hotel.operations.customers import CustomerCreateData

    return CustomerCreateData(
        first_name="John",
        last_name="Doe",
        email_address="john.doe@example.com",
    )


@pytest.fixture
def sample_customer_update_data():
    """Provide sample customer update data."""
    from hotel.operations.customers import CustomerUpdateData

    return CustomerUpdateData(
        first_name="Jane",
        email_address="jane.doe@example.com",
    )
