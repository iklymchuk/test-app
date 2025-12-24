from hotel.db import engine
from hotel.db.models import DBRoom, to_dict


def read_all_rooms():
    session = engine.DBSession()
    rooms = session.query(DBRoom).all()
    return [to_dict(room) for room in rooms]


def read_room_by_id(room_id: int):
    session = engine.DBSession()
    # room = session.query(DBRoom).filter(DBRoom.id == room_id).first()
    # room = session.get(DBRoom, room_id)
    room = session.query(DBRoom).get(room_id)
    return to_dict(room)
