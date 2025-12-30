"""
Integration test fixtures.

DESIGN PATTERNS IMPLEMENTED:
1. Fixture Factory Pattern - Reusable test data builders
2. Test Database Pattern - Isolated test database per test
3. Setup/Teardown Pattern - Clean state management
4. Dependency Injection - Fixtures inject dependencies
5. Session Management Pattern - Transaction-based test isolation

ARCHITECTURE:
- Fixtures provide isolated test environment
- Each test gets fresh database state
- No test pollution or side effects
- Mimics production environment structure
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from hotel.db.models import Base, DBCustomer, DBRoom, DBBooking
from hotel.db.db_interface import DBInterface


# ============================================================================
# DATABASE FIXTURES - Test Database Pattern
# ============================================================================


@pytest.fixture(scope="function")
def test_db_engine():
    """
    Provide isolated in-memory SQLite database engine.

    PATTERN: Test Database Pattern
    - Each test gets a fresh database
    - In-memory for speed (no disk I/O)
    - Automatically cleaned up after test

    SCOPE: function - new database per test for isolation
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,  # Set True for SQL debugging
        connect_args={"check_same_thread": False},
    )

    # Create all tables from models
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup: dispose engine and release resources
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Session:
    """
    Provide database session with automatic rollback.

    PATTERN: Session Management Pattern
    - Transaction-based isolation
    - Automatic rollback ensures clean slate
    - No side effects between tests

    ARCHITECTURE:
    Each test operates in a transaction that's never committed,
    ensuring database state is reset after each test.
    """
    # Create session factory
    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )

    session = TestSessionLocal()

    # Provide session to test
    yield session

    # Cleanup: rollback any changes and close session
    session.rollback()
    session.close()


# ============================================================================
# DATABASE INTERFACE FIXTURES - Dependency Injection Pattern
# ============================================================================


@pytest.fixture
def booking_db_interface(test_db_session) -> DBInterface:
    """
    Provide DBInterface for bookings with test database.

    PATTERN: Dependency Injection
    - Real implementation, test database
    - No mocking - testing actual database operations
    """
    return DBInterface(DBBooking, session=test_db_session)


@pytest.fixture
def customer_db_interface(test_db_session) -> DBInterface:
    """Provide DBInterface for customers with test database."""
    return DBInterface(DBCustomer, session=test_db_session)


@pytest.fixture
def room_db_interface(test_db_session) -> DBInterface:
    """Provide DBInterface for rooms with test database."""
    return DBInterface(DBRoom, session=test_db_session)


# ============================================================================
# TEST DATA FACTORIES - Factory Pattern
# ============================================================================


@pytest.fixture
def customer_factory(test_db_session):
    """
    Factory for creating test customers in database.

    PATTERN: Test Data Builder / Factory Pattern
    - Encapsulates test data creation
    - Provides sensible defaults
    - Allows customization when needed

    USAGE:
        customer = customer_factory(first_name="Alice")
        customer = customer_factory()  # Uses defaults
    """

    def _create_customer(
        first_name: str = "Test", last_name: str = "Customer", email_address: str = None
    ) -> DBCustomer:
        if email_address is None:
            email_address = f"{first_name.lower()}.{last_name.lower()}@example.com"

        customer = DBCustomer(
            first_name=first_name, last_name=last_name, email_address=email_address
        )
        test_db_session.add(customer)
        test_db_session.commit()
        test_db_session.refresh(customer)
        return customer

    return _create_customer


@pytest.fixture
def room_factory(test_db_session):
    """
    Factory for creating test rooms in database.

    PATTERN: Test Data Builder Pattern
    Provides flexible room creation with sensible defaults.
    """

    def _create_room(number: str = None, size: int = 25, price: int = 100) -> DBRoom:
        # Auto-generate room number if not provided
        if number is None:
            count = test_db_session.query(DBRoom).count()
            number = f"{100 + count + 1}"

        room = DBRoom(number=number, size=size, price=price)
        test_db_session.add(room)
        test_db_session.commit()
        test_db_session.refresh(room)
        return room

    return _create_room


@pytest.fixture
def booking_factory(test_db_session, customer_factory, room_factory):
    """
    Factory for creating test bookings in database.

    PATTERN: Composite Factory Pattern
    - Uses other factories to create dependencies
    - Handles complex object graphs
    - Ensures referential integrity

    ARCHITECTURE:
    Automatically creates required customer and room if not provided,
    demonstrating proper handling of foreign key relationships.
    """

    def _create_booking(
        customer: DBCustomer = None,
        room: DBRoom = None,
        from_date: date = None,
        to_date: date = None,
        price: int = None,
    ) -> DBBooking:
        # Create dependencies if not provided
        if customer is None:
            customer = customer_factory()
        if room is None:
            room = room_factory()

        # Set default dates if not provided
        if from_date is None:
            from_date = date.today()
        if to_date is None:
            to_date = from_date + timedelta(days=3)

        # Calculate price if not provided
        if price is None:
            days = (to_date - from_date).days
            price = days * room.price

        booking = DBBooking(
            customer_id=customer.id,
            room_id=room.id,
            from_date=from_date,
            to_date=to_date,
            price=price,
        )
        test_db_session.add(booking)
        test_db_session.commit()
        test_db_session.refresh(booking)
        return booking

    return _create_booking


# ============================================================================
# PRE-POPULATED TEST DATA FIXTURES - Fixture Setup Pattern
# ============================================================================


@pytest.fixture
def sample_customers(customer_factory):
    """
    Provide a set of pre-created customers for tests.

    PATTERN: Fixture Setup Pattern
    - Pre-populates database with common test data
    - Reduces boilerplate in tests
    - Represents realistic data scenarios
    """
    return [
        customer_factory(first_name="Alice", last_name="Johnson"),
        customer_factory(first_name="Bob", last_name="Smith"),
        customer_factory(first_name="Charlie", last_name="Brown"),
    ]


@pytest.fixture
def sample_rooms(room_factory):
    """
    Provide a set of pre-created rooms for tests.

    Represents different room types: standard, deluxe, suite.
    """
    return [
        room_factory(number="101", size=20, price=100),  # Standard
        room_factory(number="201", size=30, price=150),  # Deluxe
        room_factory(number="301", size=50, price=250),  # Suite
    ]


@pytest.fixture
def sample_bookings(booking_factory, sample_customers, sample_rooms):
    """
    Provide pre-created bookings with relationships.

    PATTERN: Related Data Setup Pattern
    - Creates complex object graphs
    - Tests with realistic relationships
    - Demonstrates foreign key handling
    """
    today = date.today()

    return [
        booking_factory(
            customer=sample_customers[0],
            room=sample_rooms[0],
            from_date=today,
            to_date=today + timedelta(days=2),
        ),
        booking_factory(
            customer=sample_customers[1],
            room=sample_rooms[1],
            from_date=today + timedelta(days=5),
            to_date=today + timedelta(days=8),
        ),
    ]


# ============================================================================
# HELPER FIXTURES - Utility Pattern
# ============================================================================


@pytest.fixture
def db_query_helper(test_db_session):
    """
    Provide helper for direct database queries in tests.

    PATTERN: Test Helper Pattern
    Useful for verification and assertions on database state.
    """

    class DBQueryHelper:
        """Helper class for common database queries in tests."""

        def count_customers(self) -> int:
            """Get total number of customers in database."""
            return test_db_session.query(DBCustomer).count()

        def count_rooms(self) -> int:
            """Get total number of rooms in database."""
            return test_db_session.query(DBRoom).count()

        def count_bookings(self) -> int:
            """Get total number of bookings in database."""
            return test_db_session.query(DBBooking).count()

        def get_customer_by_email(self, email: str) -> DBCustomer:
            """Find customer by email address."""
            return (
                test_db_session.query(DBCustomer).filter_by(email_address=email).first()
            )

        def get_room_by_number(self, number: str) -> DBRoom:
            """Find room by room number."""
            return test_db_session.query(DBRoom).filter_by(number=number).first()

    return DBQueryHelper()
