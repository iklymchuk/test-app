from datetime import date
from pydantic import BaseModel
from hotel.db import engine
from hotel.db.models import DBBooking, DBRoom, to_dict

class InvalidDateError(Exception):
    pass

class BookingCreateData(BaseModel):
    room_id: int
    customer_id: int
    from_date: date
    to_date: date
    
    


def read_all_bookings():
    session = engine.DBSession()
    bookings = session.query(DBBooking).all()
    return [to_dict(booking) for booking in bookings]


def read_booking_by_id(booking_id: int):
    session = engine.DBSession()
    booking = session.query(DBBooking).get(booking_id)
    return to_dict(booking)


def create_booking(data: BookingCreateData):
    session = engine.DBSession()

    room = session.query(DBRoom).get(data.room_id)
    days = (data.to_date - data.from_date).days
    if days <= 0:
        raise InvalidDateError("Invalid booking dates")
    booking_dict = data.model_dump()
    booking_dict['price'] = room.price * days

    booking = DBBooking(**booking_dict)
    session.add(booking)
    session.commit()
    return to_dict(booking)

def delete_booking(booking_id: int):
    session = engine.DBSession()
    booking = session.query(DBBooking).get(booking_id)
    session.delete(booking)
    session.commit()
    return to_dict(booking)
