"""
Unit Tests for Room Operations

TESTING APPROACH:
- Tests business logic in isolation using stub interfaces
- No database or external dependencies
- Fast execution, focused on operation layer logic
- Validates read operations and data structure

DESIGN PATTERNS:
1. Stub Pattern - Test doubles replace database interface
2. Arrange-Act-Assert (AAA) - Clear test structure
3. Data Validation - Ensures correct data flow
4. Structure Verification - Validates response format

ARCHITECTURE:
Operations (business logic) → Stub Interface (fake data)

This is the LOWEST level of testing - pure unit tests.
"""

import pytest
from hotel.operations.rooms import (
    read_all_rooms,
    read_room_by_id,
)
from hotel.tests.utils import assert_room_valid, room_sample


@pytest.mark.unit
@pytest.mark.room
class TestRoomOperations:
    """
    Unit tests for room operations.

    SCOPE: Business logic layer (operations/)
    PATTERN: Isolated testing with stubs
    """

    def test_read_all_rooms(self, room_stub):
        """Verify read_all_rooms returns complete room list."""

        result = read_all_rooms(room_stub)

        assert len(result) == 3

        for room in result:
            assert_room_valid(room)  # Validate structure

        expected_rooms = [
            room_sample(),
            room_sample({"id": 2, "number": "102", "size": 25, "price": 120}),
            room_sample({"id": 3, "number": "103", "size": 30, "price": 150}),
        ]
        for room, expected in zip(result, expected_rooms):
            for key, value in expected.items():
                assert room[key] == value

    def test_read_room_by_id(self, room_stub):
        """Verify read_room_by_id retrieves correct room data."""

        result = read_room_by_id(1, room_stub)

        assert result is not None
        assert_room_valid(result)  # Assert - Structure valid
        expected = room_sample()
        for key, value in expected.items():
            assert result[key] == value

    def test_read_room_by_different_id(self, room_stub):
        """Verify read_room_by_id handles different ID correctly."""

        result = read_room_by_id(5, room_stub)

        assert result is not None
        assert_room_valid(result)  # Assert - Structure valid
        expected = room_sample({"id": 5})
        for key, value in expected.items():
            assert result[key] == value
