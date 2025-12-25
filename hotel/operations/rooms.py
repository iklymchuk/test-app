from hotel.operations.interface import DataInterface, DataObject


def read_all_rooms(room_interface: DataInterface) -> list[DataObject]:
    return room_interface.read_all()


def read_room_by_id(room_id: int, room_interface: DataInterface) -> DataObject:
    return room_interface.read_by_id(room_id)
