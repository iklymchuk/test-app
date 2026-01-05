from fastapi import APIRouter

from hotel.db.db_interface import DBInterface
from hotel.db.models import DBCustomer
from hotel.operations.customers import (
    CustomerCreateData,
    CustomerUpdateData,
    create_customer,
    read_all_customers,
    read_customer_by_id,
    update_customer,
)


router = APIRouter()


@router.get("/customers", operation_id="get_all_customers")
def api_read_all_customers():
    customerInterface = DBInterface(DBCustomer)
    return read_all_customers(customerInterface)


@router.get("/customer/{customer_id}", operation_id="get_customer_by_id")
def api_read_customer_by_id(customer_id: int):
    customerInterface = DBInterface(DBCustomer)
    return read_customer_by_id(customer_id, customerInterface)


@router.post("/customer", operation_id="create_customer")
def api_create_customer(customer: CustomerCreateData):
    customerInterface = DBInterface(DBCustomer)
    return create_customer(customer, customerInterface)


@router.patch("/customer/{customer_id}", operation_id="update_customer")
def api_update_customer(customer_id: int, customer: CustomerUpdateData):
    customerInterface = DBInterface(DBCustomer)
    return update_customer(customer_id, customer, customerInterface)
