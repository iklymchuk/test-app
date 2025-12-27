"""
Unit tests for room operations using RoomStubInterface.
Testing business logic with inheritance-based stubs.
"""

import pytest
from hotel.operations.rooms import (
    read_all_rooms,
    read_room_by_id,
)
from hotel.tests.utils import assert_room_valid


@pytest.mark.unit
@pytest.mark.room
class TestRoomOperations:
    """Test room operations with stub data."""

    def test_read_all_rooms(self, room_stub):
        """Test reading all rooms returns stubbed data."""

        result = read_all_rooms(room_stub)

        assert len(result) == 3

        for room in result:
            assert_room_valid(room)  # Validate structure

        assert result[0]["id"] == 1
        assert result[0]["number"] == "101"
        assert result[0]["size"] == 20
        assert result[0]["price"] == 100
        assert result[1]["id"] == 2
        assert result[1]["number"] == "102"
        assert result[1]["price"] == 120
        assert result[2]["id"] == 3
        assert result[2]["number"] == "103"
        assert result[2]["size"] == 30
        assert result[2]["price"] == 150

    def test_read_room_by_id(self, room_stub):
        """Test reading a specific room by ID."""

        result = read_room_by_id(1, room_stub)

        assert result is not None
        assert_room_valid(result)  # Assert - Structure valid
        assert result["number"] == "Stub Room"
        assert result["size"] == 20
        assert result["price"] == 100

    def test_read_room_by_different_id(self, room_stub):
        """Test reading a room with different ID."""

        result = read_room_by_id(5, room_stub)

        assert result is not None
        assert_room_valid(result)  # Assert - Structure valid
        assert result["id"] == 5
        assert result["number"] == "Stub Room"
