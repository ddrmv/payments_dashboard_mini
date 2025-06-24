#!/usr/bin/env python
"""
Database Clearing Script

This script clears all existing data from the database tables.
It deletes data in the correct order to respect foreign key constraints.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import SQLAlchemy components
from payments.db import close_session, get_session
from payments.sqlalchemy_models import Customer, Payment, Purchase, Service
from sqlalchemy import text


# def clear_database(session):
#     """Clear all existing data from the database tables."""
#     print("Clearing existing data...")

#     # Delete in reverse order to respect foreign key constraints
#     session.query(Payment).delete()
#     session.query(Purchase).delete()
#     session.query(Service).delete()
#     session.query(Customer).delete()
#     session.commit()

#     print("Database cleared successfully.")


def clear_database(session):
    """Clear all data from database tables using TRUNCATE."""
    print("Clearing existing data with TRUNCATE...")
    session.execute(
        text(
            "TRUNCATE TABLE payments, purchases, services, customers RESTART IDENTITY CASCADE"
        )
    )
    session.commit()
    print("Database cleared successfully.")


def print_clearance_statistics(session):
    """Print statistics after clearing the database."""
    print("\n" + "=" * 50)
    print("DATABASE CLEARANCE COMPLETED SUCCESSFULLY!")
    print("=" * 50)

    # Count records (should all be 0)
    customer_count = session.query(Customer).count()
    service_count = session.query(Service).count()
    purchase_count = session.query(Purchase).count()
    payment_count = session.query(Payment).count()

    print(f"Remaining customers: {customer_count:,}")
    print(f"Remaining services: {service_count}")
    print(f"Remaining purchases: {purchase_count:,}")
    print(f"Remaining payments: {payment_count:,}")

    if (
        customer_count == 0
        and service_count == 0
        and purchase_count == 0
        and payment_count == 0
    ):
        print("\n✅ All tables have been successfully cleared!")
    else:
        print("\n⚠️  Some tables still contain data!")


def main():
    """Main function to clear the database."""
    start_time = datetime.now()
    print("Starting database clearance...")
    print("=" * 60)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    session = None
    try:
        # Get SQLAlchemy session
        session = get_session()

        # Clear existing data
        clear_database(session)

        # Print statistics
        print_clearance_statistics(session)

        # Calculate end time and elapsed time
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        print("\n" + "=" * 60)
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print("=" * 60)

    except Exception as e:
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        print(
            f"\nError during database clearance after {elapsed_time:.2f} seconds: {e}"
        )
        if session:
            session.rollback()
        sys.exit(1)
    finally:
        if session:
            close_session(session)


if __name__ == "__main__":
    main()
