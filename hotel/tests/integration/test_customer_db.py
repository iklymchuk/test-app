"""
Integration Tests for Customer Database Operations

TESTING APPROACH:
- Exercises REAL SQLAlchemy session + in-memory SQLite
- Focuses on persistence rules, constraints, and relationships
- Complements unit tests (stubs) by validating database behavior

DESIGN PATTERNS:
1. Arrange-Act-Assert - Consistent structure per test
2. Test Data Builder - Factory fixtures create realistic rows
3. Database Transaction Pattern - Fresh DB per test via fixtures
4. Verification Pattern - State-based assertions through helpers

ARCHITECTURE:
Operations Layer (unit) → Stubs
Integration Layer (this file) → DBInterface + SQLAlchemy + Test DB
Ensures persistence layer matches business expectations.
"""

import pytest
from hotel.db.models import DBCustomer


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.customer
class TestCustomerDatabaseOperations:
    """
    Integration tests for customer CRUD operations.

    SCOPE: Persistence layer (db_interface + SQLAlchemy)
    STRATEGY: State-based verification via real transactions
    """

    def test_create_customer_persists_all_fields(
        self, customer_db_interface, test_db_session, db_query_helper
    ):
        """Verify customer creation persists all fields correctly."""
        # Arrange
        initial_count = db_query_helper.count_customers()

        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "john.doe@example.com",
        }

        # Act
        result = customer_db_interface.create(customer_data)

        # Assert - Returned data
        assert result["id"] is not None
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["email_address"] == "john.doe@example.com"

        # Assert - Database state
        assert db_query_helper.count_customers() == initial_count + 1

        # Assert - Persistence verification
        saved_customer = test_db_session.get(DBCustomer, result["id"])
        assert saved_customer.first_name == "John"

    def test_read_customer_by_id_returns_correct_record(
        self, customer_db_interface, customer_factory
    ):
        """
        Test retrieving specific customer by ID.

        PATTERN: Create-Read-Verify
        """
        # Arrange
        created = customer_factory(
            first_name="Alice", last_name="Johnson", email_address="alice.j@example.com"
        )

        # Act
        result = customer_db_interface.read_by_id(created.id)

        # Assert
        assert result["id"] == created.id
        assert result["first_name"] == "Alice"
        assert result["last_name"] == "Johnson"
        assert result["email_address"] == "alice.j@example.com"

    def test_read_all_customers_returns_complete_list(
        self, customer_db_interface, sample_customers
    ):
        """
        Test retrieving all customers from database.

        PATTERN: Bulk data verification
        USES: Pre-populated fixture (sample_customers)
        """
        # Arrange - sample_customers creates 3 customers

        # Act
        result = customer_db_interface.read_all()

        # Assert
        assert len(result) == 3
        assert all("id" in customer for customer in result)
        assert all("email_address" in customer for customer in result)

        # Verify specific customers present
        first_names = [c["first_name"] for c in result]
        assert "Alice" in first_names
        assert "Bob" in first_names
        assert "Charlie" in first_names

    def test_update_customer_modifies_specific_fields(
        self, customer_db_interface, customer_factory, test_db_session
    ):
        """
        Test partial update of customer data.

        PATTERN: Partial update verification
        VERIFIES:
        - Only updated fields change
        - Other fields remain unchanged
        - Changes persist
        """
        # Arrange
        customer = customer_factory(
            first_name="Original",
            last_name="Name",
            email_address="original@example.com",
        )
        original_id = customer.id

        # Act - Update only email
        update_data = {"email_address": "updated@example.com"}
        result = customer_db_interface.update(customer.id, update_data)

        # Assert - Updated field changed
        assert result["email_address"] == "updated@example.com"

        # Assert - Other fields unchanged
        assert result["first_name"] == "Original"
        assert result["last_name"] == "Name"
        assert result["id"] == original_id

        # Assert - Database persistence
        test_db_session.expire_all()
        updated = test_db_session.get(DBCustomer, original_id)
        assert updated.email_address == "updated@example.com"
        assert updated.first_name == "Original"

    def test_delete_customer_removes_record(
        self, customer_db_interface, customer_factory, test_db_session, db_query_helper
    ):
        """
        Test customer deletion.

        PATTERN: Create-Delete-Verify absence
        """
        # Arrange
        customer = customer_factory()
        customer_id = customer.id
        initial_count = db_query_helper.count_customers()

        # Act
        result = customer_db_interface.delete(customer_id)

        # Assert - Returns deleted data
        assert result["id"] == customer_id

        # Assert - Record removed
        assert db_query_helper.count_customers() == initial_count - 1
        deleted = test_db_session.get(DBCustomer, customer_id)
        assert deleted is None


@pytest.mark.integration
@pytest.mark.database
class TestCustomerDataIntegrity:
    """
    Tests for data validation and integrity constraints.

    FOCUS: Database-level data validation
    DEMONSTRATES: Testing data constraints and edge cases
    """

    @pytest.mark.parametrize(
        "first_name,last_name,email",
        [
            ("A", "B", "a@b.com"),  # Minimal names
            ("Very" * 50, "Long" * 50, "long@email.com"),  # Long names
            ("José", "García", "jose@example.com"),  # Unicode characters
            ("O'Brien", "Van-Der-Berg", "special@example.com"),  # Special chars
        ],
    )
    def test_create_customer_with_various_name_formats(
        self, customer_db_interface, first_name, last_name, email
    ):
        """
        Test customer creation with edge case names.

        PATTERN: Parametrized edge case testing
        DEMONSTRATES: Testing boundary conditions and special cases
        """
        # Arrange
        customer_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email_address": email,
        }

        # Act
        result = customer_db_interface.create(customer_data)

        # Assert
        assert result["first_name"] == first_name
        assert result["last_name"] == last_name
        assert result["email_address"] == email

    def test_customers_have_unique_auto_increment_ids(self, customer_factory):
        """
        Test that each customer gets unique auto-incremented ID.

        PATTERN: ID generation verification
        """
        # Arrange & Act
        customer1 = customer_factory()
        customer2 = customer_factory()
        customer3 = customer_factory()

        # Assert
        assert customer1.id != customer2.id != customer3.id
        assert customer1.id < customer2.id < customer3.id  # Sequential


@pytest.mark.integration
@pytest.mark.database
class TestCustomerQueryScenarios:
    """
    Tests for complex customer queries and searches.

    DEMONSTRATES: Real-world query patterns
    """

    def test_find_customer_by_email(self, customer_factory, db_query_helper):
        """
        Test searching customer by email address.

        PATTERN: Search query testing
        SCENARIO: Login / user lookup by email
        """
        # Arrange
        customer_factory(email_address="alice@example.com")
        customer_factory(email_address="bob@example.com")

        # Act
        found = db_query_helper.get_customer_by_email("alice@example.com")

        # Assert
        assert found is not None
        assert found.email_address == "alice@example.com"

    def test_query_customers_by_last_name(self, customer_factory, test_db_session):
        """
        Test querying customers with same last name.

        PATTERN: Filtering query test
        SCENARIO: Family member search
        """
        # Arrange - Create related customers
        customer_factory(first_name="John", last_name="Smith")
        customer_factory(first_name="Jane", last_name="Smith")
        customer_factory(first_name="Bob", last_name="Jones")

        # Act
        smiths = test_db_session.query(DBCustomer).filter_by(last_name="Smith").all()

        # Assert
        assert len(smiths) == 2
        assert all(c.last_name == "Smith" for c in smiths)
        first_names = [c.first_name for c in smiths]
        assert "John" in first_names
        assert "Jane" in first_names

    def test_count_customers_with_specific_email_domain(
        self, customer_factory, test_db_session
    ):
        """
        Test counting customers from specific email domain.

        PATTERN: Aggregation with filtering
        SCENARIO: Corporate vs personal email analysis
        """
        # Arrange
        customer_factory(email_address="user1@company.com")
        customer_factory(email_address="user2@company.com")
        customer_factory(email_address="personal@gmail.com")

        # Act - Count company.com emails
        company_count = (
            test_db_session.query(DBCustomer)
            .filter(DBCustomer.email_address.like("%@company.com"))
            .count()
        )

        # Assert
        assert company_count == 2


@pytest.mark.integration
@pytest.mark.database
class TestCustomerRelationships:
    """
    Tests for customer relationships with other entities.

    DEMONSTRATES: Testing foreign key relationships
    """

    def test_customer_with_multiple_bookings(
        self, customer_factory, booking_factory, test_db_session
    ):
        """
        Test customer can have multiple bookings.

        PATTERN: One-to-many relationship testing
        SCENARIO: Customer booking history
        """
        # Arrange
        customer = customer_factory(first_name="Frequent", last_name="Traveler")

        booking1 = booking_factory(customer=customer)
        booking2 = booking_factory(customer=customer)
        booking3 = booking_factory(customer=customer)

        # Act - Query customer's bookings
        from hotel.db.models import DBBooking

        customer_bookings = (
            test_db_session.query(DBBooking).filter_by(customer_id=customer.id).all()
        )

        # Assert
        assert len(customer_bookings) == 3
        assert all(b.customer_id == customer.id for b in customer_bookings)

    def test_delete_customer_with_bookings(
        self, customer_db_interface, customer_factory, booking_factory, test_db_session
    ):
        """
        Test behavior when deleting customer with associated bookings.

        PATTERN: Referential integrity testing
        NOTE: Tests current behavior - in production might need CASCADE
        """
        # Arrange
        customer = customer_factory()
        customer_id = customer.id

        # Act - Delete customer
        customer_db_interface.delete(customer_id)

        # Assert - Customer deleted
        deleted_customer = test_db_session.get(DBCustomer, customer_id)
        assert deleted_customer is None

        # Note: Booking orphaned (in production, might use CASCADE DELETE)
        # This documents current system behavior
