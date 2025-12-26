from hotel.db.db_interface import DataObject
from hotel.tests.stubs.stub_interface import DataStubInterface


class BookingStub(DataStubInterface):

    def read_by_id(self, id: int) -> DataObject:
        return {
            "id": id,
            "from_date": "2025-12-24",
            "to_date": "2025-12-26",
            "price": 200,
            "customer_id": 1,
            "room_id": 1,
        }

    def read_all(self) -> list[DataObject]:
        return [
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

    def create(self, data: DataObject) -> DataObject:
        booking = dict(data)
        booking["id"] = 999  # Assign a stub ID
        return booking

    def update(self, id: int, data: DataObject) -> DataObject:
        booking = dict(data)
        booking["id"] = id
        return booking
