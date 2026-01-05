from fastapi import APIRouter

from hotel.db.db_interface import DBInterface
from hotel.db.models import DBRoom
from hotel.operations.rooms import (
    read_all_rooms,
    read_room_by_id,
    create_room,
    RoomCreateData,
)

router = APIRouter()


@router.get("/rooms", operation_id="get_all_rooms")
def api_read_all_rooms():
    room_interface = DBInterface(DBRoom)
    return read_all_rooms(room_interface)


@router.get("/room/{room_id}", operation_id="get_room_by_id")
def api_read_room_by_id(room_id: int):
    room_interface = DBInterface(DBRoom)
    return read_room_by_id(room_id, room_interface)


@router.post("/room", operation_id="create_room")
def api_create_room(room: RoomCreateData):
    room_interface = DBInterface(DBRoom)
    return create_room(room, room_interface)
