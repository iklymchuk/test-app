from typing import Optional
from pydantic import BaseModel
from hotel.db import engine
from hotel.db.models import DBCustomer, to_dict


class CustomerCreateData(BaseModel):
    first_name: str
    last_name: str
    email_address: str


class CustomerUpdateData(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_address: Optional[str] = None


def read_all_customers():
    session = engine.DBSession()
    customers = session.query(DBCustomer).all()
    return [to_dict(customer) for customer in customers]


def read_customer_by_id(customer_id: int):
    session = engine.DBSession()
    customer = session.query(DBCustomer).get(customer_id)
    return to_dict(customer)


def create_customer(data: CustomerCreateData):
    session = engine.DBSession()
    customer = DBCustomer(**data.model_dump())
    session.add(customer)
    session.commit()
    return to_dict(customer)


def update_customer(customer_id: int, data: CustomerUpdateData):
    session = engine.DBSession()
    customer = session.query(DBCustomer).get(customer_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    session.commit()
    return to_dict(customer)
