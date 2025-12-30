from hotel.db.db_interface import DataObject
from hotel.tests.stubs.stub_interface import DataStubInterface


class RoomStub(DataStubInterface):
    def __init__(self, rooms: list[DataObject] | None = None) -> None:
        self._rooms = rooms or [
            {"id": 1, "number": "101", "size": 20, "price": 100},
            {"id": 2, "number": "102", "size": 25, "price": 120},
            {"id": 3, "number": "103", "size": 30, "price": 150},
        ]

    def read_by_id(self, id: int) -> DataObject:
        room = next((r for r in self._rooms if r["id"] == id), dict(self._rooms[0]))
        room["id"] = id
        return room

    def read_all(self) -> list[DataObject]:
        return [dict(r) for r in self._rooms]

    def create(self, data: DataObject) -> DataObject:
        room = dict(data)
        room["id"] = 999  # Assign a stub ID
        return room

    def update(self, id: int, data: DataObject) -> DataObject:
        room = dict(data)
        room["id"] = id
        return room

    def delete(self, id: int) -> DataObject:
        return {"id": id, "number": "Deleted Room", "size": 0, "price": 0}
