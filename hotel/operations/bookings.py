from datetime import date
from pydantic import BaseModel
from hotel.operations.interface import DataInterface, DataObject


class InvalidDateError(Exception):
    pass


class BookingCreateData(BaseModel):
    room_id: int
    customer_id: int
    from_date: date
    to_date: date


def read_all_bookings(booking_interface: DataInterface) -> list[DataObject]:
    return booking_interface.read_all()


def read_booking_by_id(booking_id: int, booking_interface: DataInterface) -> DataObject:
    return booking_interface.read_by_id(booking_id)


def create_booking(
    data: BookingCreateData,
    booking_interface: DataInterface,  # Injected dependency
    room_interface: DataInterface,  # Injected dependency
) -> DataObject:

    room = room_interface.read_by_id(
        data.room_id
    )  # Use room_interface to get room details

    days = (data.to_date - data.from_date).days
    if days <= 0:
        raise InvalidDateError("Invalid booking dates")
    booking_dict = data.model_dump()
    booking_dict["price"] = room["price"] * days
    return booking_interface.create(
        booking_dict
    )  # Use booking_interface to create booking


def delete_booking(booking_id: int, booking_interface: DataInterface) -> DataObject:
    return booking_interface.delete(booking_id)
