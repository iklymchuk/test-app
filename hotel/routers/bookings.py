from fastapi import APIRouter

from hotel.db.db_interface import DBInterface
from hotel.db.models import DBBooking, DBRoom
from hotel.operations.bookings import (
    BookingCreateData,
    create_booking,
    delete_booking,
    read_all_bookings,
    read_booking_by_id,
)


router = APIRouter()


@router.get("/bookings")
def api_read_all_bookings():
    bookingInterface = DBInterface(DBBooking)
    return read_all_bookings(bookingInterface)


@router.get("/booking/{booking_id}")
def api_read_booking_by_id(booking_id: int):
    bookingInterface = DBInterface(DBBooking)
    return read_booking_by_id(booking_id, bookingInterface)


@router.post("/booking")
def api_create_booking(booking: BookingCreateData):
    bookingInterface = DBInterface(DBBooking)  # Create booking interface
    roomInterface = DBInterface(DBRoom)  # Create room interface
    return create_booking(
        booking, bookingInterface, roomInterface
    )  # Inject both interfaces


@router.delete("/booking/{booking_id}")
def api_delete_booking(booking_id: int):
    bookingInterface = DBInterface(DBBooking)
    return delete_booking(booking_id, bookingInterface)
