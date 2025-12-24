from fastapi import APIRouter

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
    return read_all_bookings()


@router.get("/booking/{booking_id}")
def api_read_booking_by_id(booking_id: int):
    return read_booking_by_id(booking_id)

@router.post("/booking")
def api_create_booking(booking: BookingCreateData):
    return create_booking(booking)

@router.delete("/booking/{booking_id}")
def api_delete_booking(booking_id: int):
    return delete_booking(booking_id)