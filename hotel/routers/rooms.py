from fastapi import APIRouter

from hotel.db.db_interface import DBInterface
from hotel.db.models import DBRoom
from hotel.operations.rooms import read_all_rooms, read_room_by_id


router = APIRouter()


@router.get("/rooms")
def api_read_all_rooms():
    room_interface = DBInterface(DBRoom)
    return read_all_rooms(room_interface)


@router.get("/room/{room_id}")
def api_read_room_by_id(room_id: int):
    room_interface = DBInterface(DBRoom)
    return read_room_by_id(room_id, room_interface)
