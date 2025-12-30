from hotel.db.db_interface import DataObject
from hotel.tests.stubs.stub_interface import DataStubInterface


class BookingStub(DataStubInterface):
    def __init__(self, bookings: list[DataObject] | None = None) -> None:
        # Allow tests to override the fixture data while keeping sensible defaults
        self._bookings = bookings or [
            {
                "id": 1,
                "from_date": "2025-12-20",
                "to_date": "2025-12-22",
                "price": 200,
                "customer_id": 1,
                "room_id": 1,
            },
            {
                "id": 2,
                "from_date": "2025-12-23",
                "to_date": "2025-12-25",
                "price": 300,
                "customer_id": 2,
                "room_id": 2,
            },
        ]

    def read_by_id(self, id: int) -> DataObject:
        # Return matching booking or the first record with overridden id to keep tests predictable
        booking = next(
            (b for b in self._bookings if b["id"] == id), dict(self._bookings[0])
        )
        booking["id"] = id
        return booking

    def read_all(self) -> list[DataObject]:
        # Return a shallow copy to avoid mutation across tests
        return [dict(b) for b in self._bookings]

    def create(self, data: DataObject) -> DataObject:
        booking = dict(data)
        booking["id"] = 999  # Assign a stub ID
        return booking

    def update(self, id: int, data: DataObject) -> DataObject:
        booking = dict(data)
        booking["id"] = id
        return booking
