from hotel.db.db_interface import DataObject
from hotel.tests.stubs.stub_interface import DataStubInterface


class CustomerStub(DataStubInterface):
    def __init__(self, customers: list[DataObject] | None = None) -> None:
        # Allow override while keeping defaults small and readable
        self._customers = customers or [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
        ]

    def read_by_id(self, id: int) -> DataObject:
        customer = next(
            (c for c in self._customers if c["id"] == id), dict(self._customers[0])
        )
        customer["id"] = id
        return customer

    def read_all(self) -> list[DataObject]:
        return [dict(c) for c in self._customers]

    def create(self, data: DataObject) -> DataObject:
        customer = dict(data)
        customer["id"] = 999  # Assign a stub ID
        return customer

    def update(self, id: int, data: DataObject) -> DataObject:
        customer = dict(data)
        customer["id"] = id
        return customer
