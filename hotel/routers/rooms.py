from fastapi import APIRouter

from hotel.operations.rooms import read_all_rooms, read_room_by_id


router = APIRouter()


@router.get("/rooms")
def api_read_all_rooms():
    return read_all_rooms()


@router.get("/room/{room_id}")
def api_read_room_by_id(room_id: int):
    return read_room_by_id(room_id)
