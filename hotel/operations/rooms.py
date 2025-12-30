from hotel.operations.interface import DataInterface, DataObject
from pydantic import BaseModel


class RoomCreateData(BaseModel):
    number: str
    size: int
    price: int


def read_all_rooms(room_interface: DataInterface) -> list[DataObject]:
    return room_interface.read_all()


def read_room_by_id(room_id: int, room_interface: DataInterface) -> DataObject:
    return room_interface.read_by_id(room_id)


def create_room(data: RoomCreateData, room_interface: DataInterface) -> DataObject:
    return room_interface.create(data.model_dump())
