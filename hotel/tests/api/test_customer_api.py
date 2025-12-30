"""
API Integration Tests for Customer Endpoints

TESTING APPROACH:
- Tests HTTP layer through FastAPI TestClient
- Uses REAL operations and DBInterface (no mocks/stubs)
- Tests full request → router → operations → db → response flow
- Validates HTTP status codes, request/response serialization

DESIGN PATTERNS:
1. API Integration Testing - Full stack testing with test database
2. Arrange-Act-Assert (AAA) - Clear test structure
3. Test Data Factory - api_customer fixture for setup
4. HTTP Contract Testing - Validates API contracts

ARCHITECTURE DEMONSTRATED:
HTTP → Router → Operations Interface (real) → DB Interface (real) → Test DB
"""

import pytest


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.customer
class TestCustomerAPIEndpoints:
    """
    API integration tests for customer endpoints.

    SCOPE: HTTP layer + full stack
    PATTERN: Contract testing - validates API behavior
    """

    def test_create_customer_returns_200_with_customer_data(self, api_client):
        """
        Test POST /customer creates customer and returns data.

        PATTERN: Happy path API testing
        VALIDATES:
        - HTTP status code
        - Response structure
        - Data persistence (implicitly through ID generation)
        """
        # Arrange
        customer_data = {
            "first_name": "Alice",
            "last_name": "Wonder",
            "email_address": "alice@example.com",
        }

        # Act - Make HTTP POST request
        response = api_client.post("/customer", json=customer_data)

        # Assert - HTTP response
        assert response.status_code == 200

        # Assert - Response structure
        json_data = response.json()
        assert "id" in json_data
        assert json_data["first_name"] == "Alice"
        assert json_data["last_name"] == "Wonder"
        assert json_data["email_address"] == "alice@example.com"

    def test_read_all_customers_returns_empty_list_initially(self, api_client):
        """
        Test GET /customers with no data returns empty list.

        PATTERN: Empty state testing
        """
        # Act
        response = api_client.get("/customers")

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_read_all_customers_returns_created_customers(
        self, api_client, api_customer
    ):
        """
        Test GET /customers returns all created customers.

        PATTERN: List endpoint testing
        DEMONSTRATES: Using test data factories
        """
        # Arrange - Create multiple customers via API
        customer1 = api_customer(first_name="Alice", email="alice@example.com")
        customer2 = api_customer(first_name="Bob", email="bob@example.com")

        # Act
        response = api_client.get("/customers")

        # Assert
        assert response.status_code == 200
        customers = response.json()
        assert len(customers) == 2

        # Assert - Contains both customers
        customer_ids = [c["id"] for c in customers]
        assert customer1["id"] in customer_ids
        assert customer2["id"] in customer_ids

    def test_read_customer_by_id_returns_correct_customer(
        self, api_client, api_customer
    ):
        """
        Test GET /customer/{id} returns specific customer.

        PATTERN: Detail endpoint testing
        """
        # Arrange
        created = api_customer(
            first_name="Charlie", last_name="Brown", email="charlie@example.com"
        )
        customer_id = created["id"]

        # Act
        response = api_client.get(f"/customer/{customer_id}")

        # Assert
        assert response.status_code == 200
        customer = response.json()
        assert customer["id"] == customer_id
        assert customer["first_name"] == "Charlie"
        assert customer["last_name"] == "Brown"

    def test_update_customer_modifies_data(self, api_client, api_customer):
        """
        Test POST /customer/{id} updates customer data.

        PATTERN: Update endpoint testing
        VALIDATES: Partial update functionality
        """
        # Arrange - Create customer
        created = api_customer(
            first_name="David", last_name="Original", email="david@example.com"
        )
        customer_id = created["id"]

        # Act - Update email only
        update_data = {"email_address": "david.new@example.com"}
        response = api_client.patch(f"/customer/{customer_id}", json=update_data)

        # Assert - Update response
        assert response.status_code == 200
        updated = response.json()
        assert updated["email_address"] == "david.new@example.com"
        assert updated["first_name"] == "David"  # Unchanged
        assert updated["last_name"] == "Original"  # Unchanged

        # Assert - Persistence (read back)
        get_response = api_client.get(f"/customer/{customer_id}")
        assert get_response.json()["email_address"] == "david.new@example.com"


@pytest.mark.api
@pytest.mark.integration
class TestCustomerAPIValidation:
    """
    API validation and error handling tests.

    SCOPE: HTTP validation, error responses
    NOTE: Currently routers may not have full validation
    """

    def test_create_customer_with_minimal_data(self, api_client):
        """
        Test creating customer with minimal valid data.

        PATTERN: Boundary testing
        """
        # Arrange
        minimal_data = {"first_name": "A", "last_name": "B", "email_address": "a@b.c"}

        # Act
        response = api_client.post("/customer", json=minimal_data)

        # Assert - Should succeed
        assert response.status_code == 200
        assert response.json()["first_name"] == "A"


@pytest.mark.api
@pytest.mark.integration
class TestCustomerAPIIntegration:
    """
    Full integration scenarios involving customers.

    SCOPE: Multi-endpoint workflows
    DEMONSTRATES: Real-world usage patterns
    """

    def test_create_read_update_read_workflow(self, api_client):
        """
        Test complete CRUD workflow via API.

        PATTERN: Workflow testing
        DEMONSTRATES: End-to-end API usage
        """
        # Step 1: Create
        create_response = api_client.post(
            "/customer",
            json={
                "first_name": "Emma",
                "last_name": "Watson",
                "email_address": "emma@example.com",
            },
        )
        assert create_response.status_code == 200
        customer_id = create_response.json()["id"]

        # Step 2: Read
        read_response = api_client.get(f"/customer/{customer_id}")
        assert read_response.status_code == 200
        assert read_response.json()["first_name"] == "Emma"

        # Step 3: Update
        update_response = api_client.patch(
            f"/customer/{customer_id}",
            json={"email_address": "emma.watson@example.com"},
        )
        assert update_response.status_code == 200

        # Step 4: Read again - verify update
        final_response = api_client.get(f"/customer/{customer_id}")
        assert final_response.status_code == 200
        assert final_response.json()["email_address"] == "emma.watson@example.com"

    def test_multiple_customers_independent_updates(self, api_client, api_customer):
        """
        Test that updating one customer doesn't affect others.

        PATTERN: Isolation testing
        """
        # Arrange - Create two customers
        customer1 = api_customer(first_name="Frank", email="frank@example.com")
        customer2 = api_customer(first_name="Grace", email="grace@example.com")

        # Act - Update only customer1
        api_client.patch(
            f"/customer/{customer1['id']}",
            json={"email_address": "frank.updated@example.com"},
        )

        # Assert - Customer2 unchanged
        response = api_client.get(f"/customer/{customer2['id']}")
        assert response.json()["email_address"] == "grace@example.com"
        assert response.json()["first_name"] == "Grace"
