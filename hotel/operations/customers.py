from typing import Optional
from pydantic import BaseModel
from hotel.operations.interface import DataInterface, DataObject


class CustomerCreateData(BaseModel):
    first_name: str
    last_name: str
    email_address: str


class CustomerUpdateData(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_address: Optional[str] = None


def read_all_customers(customer_interface: DataInterface) -> list[DataObject]:
    return customer_interface.read_all()


def read_customer_by_id(
    customer_id: int, customer_interface: DataInterface
) -> DataObject:
    return customer_interface.read_by_id(customer_id)


def create_customer(
    data: CustomerCreateData, customer_interface: DataInterface
) -> DataObject:
    return customer_interface.create(data.model_dump())


def update_customer(
    customer_id: int, data: CustomerUpdateData, customer_interface: DataInterface
) -> DataObject:
    return customer_interface.update(customer_id, data.model_dump())
