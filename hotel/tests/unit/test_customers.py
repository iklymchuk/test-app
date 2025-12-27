"""
Unit tests for customer operations using CustomerStubInterface.
Testing business logic with inheritance-based stubs.
"""

import pytest
from hotel.operations.customers import (
    read_all_customers,
    read_customer_by_id,
    create_customer,
    update_customer,
    CustomerUpdateData,
)
from hotel.tests.utils import assert_customer_valid


@pytest.mark.unit
@pytest.mark.customer
class TestCustomerOperations:
    """Test customer operations with stub data."""

    def test_read_all_customers(self, customer_stub):
        """Test reading all customers returns stubbed data."""

        result = read_all_customers(customer_stub)

        assert len(result) == 3

        for customer in result:
            assert_customer_valid(customer)  # Validate structure

        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        assert result[2]["id"] == 3

    def test_read_customer_by_id(self, customer_stub):
        """Test reading a specific customer by ID."""

        result = read_customer_by_id(1, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        assert result["id"] == 1
        assert result["name"] == "Stub Customer"

    def test_read_customer_by_different_id(self, customer_stub):
        """Test reading a customer with different ID."""

        result = read_customer_by_id(42, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        assert result["id"] == 42

    def test_create_customer(self, customer_stub, sample_customer_data):
        """Test creating a new customer."""

        result = create_customer(sample_customer_data, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        assert result["id"] == 999  # Stub assigns ID 999
        assert result["first_name"] == sample_customer_data.first_name
        assert result["email_address"] == sample_customer_data.email_address

    def test_update_customer(self, customer_stub, sample_customer_update_data):
        """Test updating an existing customer."""

        result = update_customer(10, sample_customer_update_data, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        assert result["id"] == 10  # ID should be preserved
        assert result["first_name"] == sample_customer_update_data.first_name

    def test_update_customer_partial(self, customer_stub):
        """Test updating only specific fields of a customer."""

        update_data = CustomerUpdateData(email_address="new.email@example.com")

        result = update_customer(5, update_data, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        assert result["id"] == 5
        assert result["email_address"] == "new.email@example.com"
