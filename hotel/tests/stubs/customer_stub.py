from hotel.db.db_interface import DataObject
from hotel.tests.stubs.stub_interface import DataStubInterface


class CustomerStub(DataStubInterface):

    def read_by_id(self, id: int) -> DataObject:
        return {"id": id, "name": "Stub Customer", "email": "stub@example.com"}

    def read_all(self) -> list[DataObject]:
        return [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
        ]

    def create(self, data: DataObject) -> DataObject:
        customer = dict(data)
        customer["id"] = 999  # Assign a stub ID
        return customer

    def update(self, id: int, data: DataObject) -> DataObject:
        customer = dict(data)
        customer["id"] = id
        return customer