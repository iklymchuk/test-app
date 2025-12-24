#!/usr/bin/env python
"""
Script to generate hotel_snap.db with sample test data
"""
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hotel.db.models import Base, DBCustomer, DBRoom, DBBooking


def generate_test_data():
    """Generate test database with sample data"""
    # Create engine and session
    engine = create_engine("sqlite:///hotel_snap.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Clear existing data
    session.query(DBBooking).delete()
    session.query(DBCustomer).delete()
    session.query(DBRoom).delete()

    # Create sample customers
    customers = [
        DBCustomer(
            first_name="John", last_name="Doe", email_address="john.doe@example.com"
        ),
        DBCustomer(
            first_name="Jane", last_name="Smith", email_address="jane.smith@example.com"
        ),
        DBCustomer(
            first_name="Robert",
            last_name="Johnson",
            email_address="robert.johnson@example.com",
        ),
        DBCustomer(
            first_name="Emily",
            last_name="Williams",
            email_address="emily.williams@example.com",
        ),
    ]
    session.add_all(customers)
    session.flush()

    # Create sample rooms
    rooms = [
        DBRoom(number="101", size=20, price=100),
        DBRoom(number="102", size=25, price=120),
        DBRoom(number="103", size=30, price=150),
        DBRoom(number="201", size=20, price=100),
        DBRoom(number="202", size=40, price=200),
        DBRoom(number="203", size=50, price=250),
    ]
    session.add_all(rooms)
    session.flush()

    # Create sample bookings
    bookings = [
        DBBooking(
            from_date=date(2025, 12, 24),
            to_date=date(2025, 12, 26),
            price=200,
            customer_id=customers[0].id,
            room_id=rooms[0].id,
        ),
        DBBooking(
            from_date=date(2025, 12, 25),
            to_date=date(2025, 12, 27),
            price=240,
            customer_id=customers[1].id,
            room_id=rooms[1].id,
        ),
        DBBooking(
            from_date=date(2025, 12, 26),
            to_date=date(2025, 12, 30),
            price=600,
            customer_id=customers[2].id,
            room_id=rooms[2].id,
        ),
        DBBooking(
            from_date=date(2025, 12, 27),
            to_date=date(2025, 12, 29),
            price=400,
            customer_id=customers[3].id,
            room_id=rooms[4].id,
        ),
    ]
    session.add_all(bookings)
    session.commit()

    print("✓ Sample data generated successfully!")
    print(f"  - {len(customers)} customers created")
    print(f"  - {len(rooms)} rooms created")
    print(f"  - {len(bookings)} bookings created")
    print("✓ Database file: hotel_snap.db")

    session.close()


if __name__ == "__main__":
    generate_test_data()
