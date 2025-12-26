from abc import ABC, abstractmethod
from hotel.operations.interface import DataObject


class DataStubInterface(ABC):
    """
    DataStubInterface (ABC) = base class for test stubs only

    Purpose: Force subclasses to implement methods via inheritance
    RoomStubInterface(DataStubInterface) - explicit inheritance
    """

    @abstractmethod
    def read_by_id(self, id: int) -> DataObject:
        pass

    @abstractmethod
    def read_all(self) -> list[DataObject]:
        pass

    @abstractmethod
    def create(self, data: DataObject) -> DataObject:
        pass

    # NOT abstract - provide default implementation
    # it is optional for subclasses to override
    def update(self, id: int, data: DataObject) -> DataObject:
        raise NotImplementedError("update() not implemented in this stub")

    # NOT abstract - provide default implementation
    # it is optional for subclasses to override
    def delete(self, id: int) -> DataObject:
        raise NotImplementedError("delete() not implemented in this stub")
