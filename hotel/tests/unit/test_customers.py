"""
Unit Tests for Customer Operations

TESTING APPROACH:
- Tests business logic in isolation using stub interfaces
- No database or external dependencies
- Fast execution, focused on operation layer logic
- Validates CRUD operations and data transformations

DESIGN PATTERNS:
1. Stub Pattern - Test doubles replace database interface
2. Arrange-Act-Assert (AAA) - Clear test structure
3. Partial Update Testing - Validates optional field updates
4. Data Validation - Ensures correct data flow

ARCHITECTURE:
Operations (business logic) → Stub Interface (fake data)

This is the LOWEST level of testing - pure unit tests.
"""

import pytest
from hotel.operations.customers import (
    read_all_customers,
    read_customer_by_id,
    create_customer,
    update_customer,
    CustomerUpdateData,
)
from hotel.tests.utils import assert_customer_valid, customer_sample


@pytest.mark.unit
@pytest.mark.customer
class TestCustomerOperations:
    """
    Unit tests for customer operations.

    SCOPE: Business logic layer (operations/)
    PATTERN: Isolated testing with stubs
    """

    def test_read_all_customers(self, customer_stub):
        """Verify read_all_customers returns complete customer list."""

        result = read_all_customers(customer_stub)

        assert len(result) == 3

        for customer in result:
            assert_customer_valid(customer)  # Validate structure

        expected_customers = [
            customer_sample(),
            customer_sample({"id": 2, "name": "Bob", "email": "bob@example.com"}),
            customer_sample(
                {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
            ),
        ]
        for customer, expected in zip(result, expected_customers):
            for key, value in expected.items():
                assert customer[key] == value

    def test_read_customer_by_id(self, customer_stub):
        """Verify read_customer_by_id retrieves correct customer data."""

        result = read_customer_by_id(1, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        expected = customer_sample()
        for key, value in expected.items():
            assert result[key] == value

    def test_read_customer_by_different_id(self, customer_stub):
        """Verify read_customer_by_id handles different ID correctly."""

        result = read_customer_by_id(42, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        expected = customer_sample({"id": 42})
        for key, value in expected.items():
            assert result[key] == value

    def test_create_customer(self, customer_stub, sample_customer_data):
        """Verify create_customer returns customer with generated ID."""

        result = create_customer(sample_customer_data, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        assert result["id"] == 999  # Stub assigns ID 999
        assert result["first_name"] == sample_customer_data.first_name
        assert result["email_address"] == sample_customer_data.email_address

    def test_update_customer(self, customer_stub, sample_customer_update_data):
        """Verify update_customer modifies customer data correctly."""

        result = update_customer(10, sample_customer_update_data, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        assert result["id"] == 10  # ID should be preserved
        assert result["first_name"] == sample_customer_update_data.first_name

    def test_update_customer_partial(self, customer_stub):
        """Verify partial update preserves unmodified fields."""

        update_data = CustomerUpdateData(email_address="new.email@example.com")

        result = update_customer(5, update_data, customer_stub)

        assert result is not None
        assert_customer_valid(result)  # Validates structure
        assert result["id"] == 5
        assert result["email_address"] == "new.email@example.com"
