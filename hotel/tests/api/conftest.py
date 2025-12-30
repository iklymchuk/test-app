"""
API Integration Test Fixtures

ARCHITECTURE:
- FastAPI TestClient for HTTP requests
- Real operations interfaces (no stubs)
- Real DBInterface with test database session
- In-memory SQLite for isolation

PATTERN: Dependency Injection
- Same interfaces as production
- Only difference: test database instead of production database
- Tests full HTTP → Router → Operations → DB flow

BENEFITS:
- Tests actual request/response cycle
- Validates routing configuration
- Tests serialization/deserialization
- Ensures layer integration works
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from hotel.db.models import Base
from hotel.db import engine as engine_module
from hotel.routers import bookings, customers, rooms


@pytest.fixture(scope="function")
def test_api_engine():
    """
    Create in-memory database engine for API tests.

    PATTERN: Test Database Pattern
    - Each test function gets fresh database
    - Complete isolation between tests
    - Fast execution (in-memory)

    SCOPE: function (new DB per test)

    NOTE: Using StaticPool to ensure all connections use the same
    in-memory database. Without this, each connection would get
    a different in-memory database.
    """
    # Create in-memory test database with StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Critical for in-memory testing!
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Initialize global engine for the app to use
    # (Routers create DBInterface without session, so they use global engine)
    engine_module.engine = engine
    engine_module.DBSession = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    yield engine

    # Cleanup - reset global state
    engine_module.engine = None
    engine_module.DBSession = None

    # Drop tables and dispose engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def api_client(test_api_engine):
    """
    FastAPI TestClient for making HTTP requests.

    PATTERN: API Integration Testing
    - Simulates HTTP requests without running server
    - Uses test database through global engine
    - Tests full request → response cycle
    - Fresh client per test ensures isolation

    ARCHITECTURE:
    HTTP Request → Router → Operations (real) → DBInterface (real) → Test DB

    NO MOCKS, NO STUBS - Testing actual integration!

    NOTE: We create a fresh FastAPI app without lifespan for tests,
    since the test_api_engine fixture already initializes the database.
    """
    # Create test app without lifespan (which would reinit DB)
    test_app = FastAPI()
    test_app.include_router(rooms.router)
    test_app.include_router(customers.router)
    test_app.include_router(bookings.router)

    # Create fresh client for each test
    client = TestClient(test_app)
    yield client
    client.close()


@pytest.fixture
def api_customer(api_client):
    """
    Factory fixture to create customer via API.

    PATTERN: Test Data Factory via API
    - Creates customers through actual API endpoints
    - Returns full response data
    - Useful for setting up test scenarios
    """

    def _create_customer(first_name="Test", last_name="Customer", email=None):
        if email is None:
            import random

            email = f"test{random.randint(1000, 9999)}@example.com"

        response = api_client.post(
            "/customer",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email_address": email,
            },
        )
        assert response.status_code == 200
        return response.json()

    return _create_customer


@pytest.fixture
def api_room(api_client):
    """
    Factory fixture to create room via API.

    PATTERN: Test Data Factory via API
    """

    def _create_room(number=None, size=25, price=100):
        if number is None:
            import random

            number = f"TEST{random.randint(100, 999)}"

        response = api_client.post(
            "/room", json={"number": number, "size": size, "price": price}
        )
        assert response.status_code == 200
        return response.json()

    return _create_room


@pytest.fixture
def api_booking(api_client, api_customer, api_room):
    """
    Factory fixture to create booking via API.

    PATTERN: Composite Test Data Factory
    - Creates all dependencies (customer, room)
    - Returns complete booking data
    """

    def _create_booking(
        customer_id=None, room_id=None, from_date="2025-12-25", to_date="2025-12-28"
    ):
        # Create dependencies if not provided
        if customer_id is None:
            customer = api_customer()
            customer_id = customer["id"]

        if room_id is None:
            room = api_room()
            room_id = room["id"]

        response = api_client.post(
            "/booking",
            json={
                "customer_id": customer_id,
                "room_id": room_id,
                "from_date": from_date,
                "to_date": to_date,
            },
        )
        assert response.status_code == 200
        return response.json()

    return _create_booking
