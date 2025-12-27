"""
Common test utilities and helper functions.

This module contains reusable test helpers that don't fit into fixtures.
"""

from typing import Any, Dict
from datetime import date, timedelta


# ============================================================================
# Assertion Helpers
# ============================================================================


def assert_booking_valid(booking: Dict[str, Any]) -> None:
    """
    Assert that a booking dictionary has all required fields.

    Args:
        booking: Booking dictionary to validate

    Raises:
        AssertionError: If booking is invalid
    """
    required_fields = ["id", "from_date", "to_date", "price", "customer_id", "room_id"]
    for field in required_fields:
        assert field in booking, f"Booking missing required field: {field}"

    assert isinstance(booking["id"], int), "Booking ID must be an integer"
    assert booking["price"] >= 0, "Booking price must be non-negative"


def assert_customer_valid(customer: Dict[str, Any]) -> None:
    """
    Assert that a customer dictionary has all required fields.

    Args:
        customer: Customer dictionary to validate

    Raises:
        AssertionError: If customer is invalid
    """
    required_fields = ["id"]
    for field in required_fields:
        assert field in customer, f"Customer missing required field: {field}"

    assert isinstance(customer["id"], int), "Customer ID must be an integer"


def assert_room_valid(room: Dict[str, Any]) -> None:
    """
    Assert that a room dictionary has all required fields.

    Args:
        room: Room dictionary to validate

    Raises:
        AssertionError: If room is invalid
    """
    required_fields = ["id", "number", "size", "price"]
    for field in required_fields:
        assert field in room, f"Room missing required field: {field}"

    assert isinstance(room["id"], int), "Room ID must be an integer"
    assert room["price"] >= 0, "Room price must be non-negative"
    assert room["size"] > 0, "Room size must be positive"


# ============================================================================
# Data Builders
# ============================================================================


def build_booking_dict(
    booking_id: int = 1,
    room_id: int = 1,
    customer_id: int = 1,
    from_date: date = None,
    to_date: date = None,
    price: int = 100,
) -> Dict[str, Any]:
    """
    Build a booking dictionary with default or custom values.

    Args:
        booking_id: Booking ID
        room_id: Room ID
        customer_id: Customer ID
        from_date: Start date (defaults to today)
        to_date: End date (defaults to 3 days from start)
        price: Total price

    Returns:
        Complete booking dictionary
    """
    if from_date is None:
        from_date = date.today()
    if to_date is None:
        to_date = from_date + timedelta(days=3)

    return {
        "id": booking_id,
        "room_id": room_id,
        "customer_id": customer_id,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "price": price,
    }


def build_customer_dict(
    customer_id: int = 1,
    first_name: str = "John",
    last_name: str = "Doe",
    email: str = "john.doe@example.com",
) -> Dict[str, Any]:
    """
    Build a customer dictionary with default or custom values.

    Args:
        customer_id: Customer ID
        first_name: First name
        last_name: Last name
        email: Email address

    Returns:
        Complete customer dictionary
    """
    return {
        "id": customer_id,
        "first_name": first_name,
        "last_name": last_name,
        "email_address": email,
    }


def build_room_dict(
    room_id: int = 1,
    number: str = "101",
    size: int = 20,
    price: int = 100,
) -> Dict[str, Any]:
    """
    Build a room dictionary with default or custom values.

    Args:
        room_id: Room ID
        number: Room number
        size: Room size in square meters
        price: Price per night

    Returns:
        Complete room dictionary
    """
    return {
        "id": room_id,
        "number": number,
        "size": size,
        "price": price,
    }