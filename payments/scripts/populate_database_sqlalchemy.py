#!/usr/bin/env python
"""
High-Performance Database Population Script using SQLAlchemy

This script populates the main database with (see constants below for numbers):
- customers
- telecom/mobile/internet services
- purchases (using existing customers and services with normal distribution)
- payments (using existing customers and purchases)

It uses SQLAlchemy with bulk operations for maximum performance.
"""

import os
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta

import numpy as np
from faker import Faker

# from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text

# Add the project root to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import SQLAlchemy components
from payments.db import close_session, get_session
from payments.sqlalchemy_models import (
    AccountStatus,
    BillingCycle,
    Currency,
    Customer,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Purchase,
    PurchaseStatus,
    Service,
    ServiceType,
)

# Initialize Faker
fake = Faker()

# Constants high performance
N_CUSTOMERS = 200_000
N_SERVICES = 20
N_PURCHASES = 200_000
N_PAYMENTS = 200_000

# # Constants low performance
# N_CUSTOMERS = 20_000
# N_SERVICES = 20
# N_PURCHASES = 20_000
# N_PAYMENTS = 20_000

# Custom telecom service names
TELECOM_SERVICES = [
    # Internet Services
    "Fiber Optic 100Mbps",
    "Fiber Optic 500Mbps",
    "Fiber Optic 1Gbps",
    "Cable Internet 50Mbps",
    "Cable Internet 200Mbps",
    "DSL Internet 25Mbps",
    "DSL Internet 50Mbps",
    "Wireless Internet 100Mbps",
    # Mobile Services
    "Mobile Plan 5GB",
    "Mobile Plan 10GB",
    "Mobile Plan 20GB",
    "Mobile Plan Unlimited",
    "Mobile Plan Family 4GB",
    "Mobile Plan Family 10GB",
    "Mobile Plan Business 50GB",
    # TV Services
    "Basic TV Package",
    "Premium TV Package",
    "Sports TV Package",
    "Movie TV Package",
    "Family TV Package",
]

# Service popularity weights (higher = more popular)
SERVICE_POPULARITY_WEIGHTS = [
    0.15,  # Fiber Optic 100Mbps - very popular
    0.12,  # Fiber Optic 500Mbps - popular
    0.08,  # Fiber Optic 1Gbps - premium
    0.10,  # Cable Internet 50Mbps - popular
    0.09,  # Cable Internet 200Mbps - popular
    0.06,  # DSL Internet 25Mbps - basic
    0.05,  # DSL Internet 50Mbps - basic
    0.04,  # Wireless Internet 100Mbps - niche
    0.12,  # Mobile Plan 5GB - very popular
    0.10,  # Mobile Plan 10GB - popular
    0.08,  # Mobile Plan 20GB - popular
    0.06,  # Mobile Plan Unlimited - premium
    0.08,  # Mobile Plan Family 4GB - family
    0.06,  # Mobile Plan Family 10GB - family
    0.03,  # Mobile Plan Business 50GB - business
    0.08,  # Basic TV Package - popular
    0.06,  # Premium TV Package - premium
    0.05,  # Sports TV Package - niche
    0.04,  # Movie TV Package - niche
    0.06,  # Family TV Package - family
]

# Normalize weights to sum to 1
SERVICE_POPULARITY_WEIGHTS = np.array(SERVICE_POPULARITY_WEIGHTS)
SERVICE_POPULARITY_WEIGHTS = (
    SERVICE_POPULARITY_WEIGHTS / SERVICE_POPULARITY_WEIGHTS.sum()
)


def clear_database(session):
    """Clear all existing data from the database tables."""
    print("Clearing existing data...")

    # Delete in reverse order to respect foreign key constraints
    session.query(Payment).delete()
    session.query(Purchase).delete()
    session.query(Service).delete()
    session.query(Customer).delete()
    session.commit()

    print("Database cleared successfully.")


def create_customers_bulk(session, n_customers=N_CUSTOMERS):
    """Create customers using bulk insert for maximum performance."""
    print(f"Creating {n_customers} customers using bulk insert...")

    # Generate customer data using pandas for efficiency
    customers_data = []
    for i in range(n_customers):
        customers_data.append(
            {
                "name": f"customer_{i}",
                "email": f"customer_{i}@example.com",
                "account_status": random.choice(list(AccountStatus)).value,
            }
        )

        if (i + 1) % 10000 == 0:
            print(f"Generated {i + 1} customer records...")

    # Bulk insert customers
    customers = [Customer(**data) for data in customers_data]
    session.bulk_save_objects(customers)
    session.commit()

    print(f"Successfully created {len(customers)} customers.")
    return customers


def create_custom_services_bulk(session):
    """Create custom telecom services with predefined names and realistic pricing."""
    print(f"Creating {len(TELECOM_SERVICES)} custom telecom services...")

    services_data = []
    for i, service_name in enumerate(TELECOM_SERVICES):
        # Determine service type based on name
        if (
            "Internet" in service_name
            or "Fiber" in service_name
            or "Cable" in service_name
            or "DSL" in service_name
            or "Wireless" in service_name
        ):
            service_type = ServiceType.INTERNET
            # Higher speeds = higher prices
            if "1Gbps" in service_name:
                base_price = round(random.uniform(80, 120), 2)
            elif "500Mbps" in service_name:
                base_price = round(random.uniform(50, 80), 2)
            elif "200Mbps" in service_name:
                base_price = round(random.uniform(40, 60), 2)
            elif "100Mbps" in service_name:
                base_price = round(random.uniform(25, 45), 2)
            elif "50Mbps" in service_name:
                base_price = round(random.uniform(20, 35), 2)
            else:  # 25Mbps
                base_price = round(random.uniform(15, 25), 2)
            is_recurring = True
            billing_cycle = BillingCycle.MONTHLY
        elif "Mobile" in service_name:
            service_type = ServiceType.MOBILE
            # More data = higher prices
            if "Unlimited" in service_name:
                base_price = round(random.uniform(40, 60), 2)
            elif "50GB" in service_name:
                base_price = round(random.uniform(35, 50), 2)
            elif "20GB" in service_name:
                base_price = round(random.uniform(25, 35), 2)
            elif "10GB" in service_name:
                base_price = round(random.uniform(20, 30), 2)
            elif "5GB" in service_name:
                base_price = round(random.uniform(15, 25), 2)
            else:  # Family plans
                base_price = round(random.uniform(30, 45), 2)
            is_recurring = True
            billing_cycle = BillingCycle.MONTHLY
        else:  # TV services
            service_type = ServiceType.TV
            if "Premium" in service_name:
                base_price = round(random.uniform(30, 50), 2)
            elif "Sports" in service_name or "Movie" in service_name:
                base_price = round(random.uniform(20, 35), 2)
            else:  # Basic and Family
                base_price = round(random.uniform(15, 25), 2)
            is_recurring = True
            billing_cycle = BillingCycle.MONTHLY

        services_data.append(
            {
                "name": service_name,
                "type": service_type.value,  # Use .value for integer
                "base_price": base_price,
                "is_recurring": is_recurring,
                "billing_cycle": billing_cycle.value,  # Use .value for integer
            }
        )

    # Bulk insert services
    services = [Service(**data) for data in services_data]
    session.bulk_save_objects(services)
    session.commit()

    print(f"Successfully created {len(services)} custom telecom services.")
    return services


def create_purchases_bulk(session, n_purchases=N_PURCHASES):
    """Create purchases using bulk insert with popularity-based service selection."""
    print(
        f"Creating {n_purchases} purchases with popularity-based service selection..."
    )

    # Get all customers and services
    customers = session.query(Customer).all()
    services = session.query(Service).all()

    if not customers or not services:
        raise ValueError("No customers or services available for purchase creation")

    # Generate purchase data
    purchases_data = []
    for i in range(n_purchases):
        # Select customer randomly
        customer = random.choice(customers)

        # Select service based on popularity weights
        service = np.random.choice(services, p=SERVICE_POPULARITY_WEIGHTS)

        # Generate dates
        start_date = datetime.now() - timedelta(days=random.randint(1, 365))
        end_date = start_date + timedelta(days=30) if service.is_recurring else None

        purchases_data.append(
            {
                "customer_id": customer.id,
                "service_id": service.id,
                "start_date": start_date,
                "end_date": end_date,
                "status": random.choice(list(PurchaseStatus)).value,
            }
        )

        if (i + 1) % 10000 == 0:
            print(f"Generated {i + 1} purchase records...")

    # Bulk insert purchases
    purchases = [Purchase(**data) for data in purchases_data]
    session.bulk_save_objects(purchases)
    session.commit()

    print(f"Successfully created {len(purchases)} purchases.")
    return purchases


def process_payment_batch(args):
    """Process a single batch of payments - standalone function for multiprocessing."""
    (
        batch_start,
        batch_size,
        n_payments,
        purchase_ids,
        purchase_customer_ids,
        service_base_prices,
        customer_ids,
    ) = args

    batch_end = min(batch_start + batch_size, n_payments)
    actual_batch_size = batch_end - batch_start

    # Convert numpy arrays to regular lists for multiprocessing
    purchase_ids = list(purchase_ids)
    purchase_customer_ids = list(purchase_customer_ids)
    service_base_prices = list(service_base_prices)
    customer_ids = list(customer_ids)

    # Randomly select purchase indices
    purchase_indices = np.random.choice(
        len(purchase_ids), size=actual_batch_size, replace=True
    )
    selected_purchase_ids = [purchase_ids[i] for i in purchase_indices]
    selected_customer_ids = [purchase_customer_ids[i] for i in purchase_indices]
    selected_base_prices = [service_base_prices[i] for i in purchase_indices]

    # Decide whether to use same customer (95%) or different customer (5%)
    same_customer_mask = np.random.random(actual_batch_size) < 0.95
    payment_customer_ids = []
    for i, same_customer in enumerate(same_customer_mask):
        if same_customer:
            payment_customer_ids.append(selected_customer_ids[i])
        else:
            payment_customer_ids.append(random.choice(customer_ids))

    # Generate other fields
    timestamps = [
        datetime.now() - timedelta(days=random.randint(1, 365))
        for _ in range(actual_batch_size)
    ]
    currencies = np.random.choice([c.value for c in Currency], size=actual_batch_size)
    payment_methods = np.random.choice(
        [m.value for m in PaymentMethod], size=actual_batch_size
    )
    statuses = np.random.choice(
        [s.value for s in PaymentStatus], size=actual_batch_size
    )

    return [
        {
            "customer_id": int(payment_customer_ids[i]),
            "purchase_id": int(selected_purchase_ids[i]),
            "amount": float(selected_base_prices[i]),
            "currency": int(currencies[i]),
            "payment_method": int(payment_methods[i]),
            "status": int(statuses[i]),
            "timestamp": timestamps[i],
        }
        for i in range(actual_batch_size)
    ]


def create_payments_bulk(session, n_payments=N_PAYMENTS, batch_size=10000):
    """Create payments using optimized bulk insert with batching and parallelism."""
    print(f"Creating {n_payments} payments with batching and parallelism...")

    # Fetch customer IDs and purchase-service pairs in chunks
    customer_ids = [c.id for c in session.query(Customer.id).yield_per(1000)]
    purchase_service_query = (
        session.query(Purchase.id, Purchase.customer_id, Service.base_price)
        .join(Service, Purchase.service_id == Service.id)
        .yield_per(1000)
    )
    purchase_service_data = [
        (p.id, p.customer_id, p.base_price) for p in purchase_service_query
    ]
    purchase_ids = [p[0] for p in purchase_service_data]
    purchase_customer_ids = [p[1] for p in purchase_service_data]
    service_base_prices = [p[2] for p in purchase_service_data]

    if not customer_ids or not purchase_ids:
        raise ValueError("No customers or purchases available for payment creation")

    # Prepare arguments for parallel processing
    batch_starts = list(range(0, n_payments, batch_size))
    process_args = [
        (
            batch_start,
            batch_size,
            n_payments,
            purchase_ids,
            purchase_customer_ids,
            service_base_prices,
            customer_ids,
        )
        for batch_start in batch_starts
    ]

    # Parallelize payment data generation
    payment_data = []
    with ProcessPoolExecutor() as executor:
        batches = executor.map(process_payment_batch, process_args)
        for i, batch in enumerate(batches):
            payment_data.extend(batch)
            print(f"Generated {(i + 1) * batch_size:,} payment records...")

    # Use raw SQL for bulk insert (example for PostgreSQL)
    def insert_batch(batch):
        session.execute(
            text("""
                INSERT INTO payments (customer_id, purchase_id, amount, currency, payment_method, status, timestamp)
                VALUES (:customer_id, :purchase_id, :amount, :currency, :payment_method, :status, :timestamp)
            """),
            batch,  # batch is already a list of dicts
        )

    # Insert payments in batches
    for i in range(0, len(payment_data), batch_size):
        batch = payment_data[i : i + batch_size]
        insert_batch(batch)
        session.commit()
        print(f"Inserted {min((i + batch_size), n_payments):,} payments...")

    print(f"Successfully created {len(payment_data)} payments.")
    return payment_data


def print_statistics(session):
    """Print final statistics about the populated database."""
    print("\n" + "=" * 50)
    print("DATABASE POPULATION COMPLETED SUCCESSFULLY!")
    print("=" * 50)

    # Count records
    customer_count = session.query(Customer).count()
    service_count = session.query(Service).count()
    purchase_count = session.query(Purchase).count()
    payment_count = session.query(Payment).count()

    print(f"Total customers: {customer_count:,}")
    print(f"Total services: {service_count}")
    print(f"Total purchases: {purchase_count:,}")
    print(f"Total payments: {payment_count:,}")

    # Service popularity statistics
    print("\nService Popularity Statistics:")
    print("-" * 50)
    services = session.query(Service).all()
    total_purchases = session.query(Purchase).count()
    for service in services:
        purchase_count = (
            session.query(Purchase).filter(Purchase.service_id == service.id).count()
        )
        popularity_percentage = (
            (purchase_count / total_purchases) * 100 if total_purchases > 0 else 0
        )
        print(
            f"{service.name}: {purchase_count:,} purchases ({popularity_percentage:.1f}%)"
        )

    # Payment verification
    print("\nPayment Verification:")
    print("-" * 50)
    total_payments = session.query(Payment).count()
    correct_amounts = 0
    matching_customers = 0

    # Sample verification (check first 1000 payments for performance)
    sample_payments = session.query(Payment).limit(1000).all()
    for payment in sample_payments:
        # Get purchase and service
        purchase = (
            session.query(Purchase).filter(Purchase.id == payment.purchase_id).first()
        )
        if purchase:
            service = (
                session.query(Service).filter(Service.id == purchase.service_id).first()
            )
            if service and abs(payment.amount - service.base_price) < 0.01:
                correct_amounts += 1
            if payment.customer_id == purchase.customer_id:
                matching_customers += 1

    sample_size = len(sample_payments)
    amount_accuracy = (correct_amounts / sample_size) * 100 if sample_size > 0 else 0
    customer_accuracy = (
        (matching_customers / sample_size) * 100 if sample_size > 0 else 0
    )

    print(f"Sample verification (first 1,000 payments):")
    print(
        f"  - Correct amounts: {correct_amounts}/{sample_size} ({amount_accuracy:.1f}%)"
    )
    print(
        f"  - Matching customers: {matching_customers}/{sample_size} ({customer_accuracy:.1f}%)"
    )


def main():
    """Main function to populate the database using SQLAlchemy."""
    start_time = datetime.now()
    print("Starting high-performance database population with SQLAlchemy...")
    print("=" * 60)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    session = None
    try:
        # Get SQLAlchemy session
        session = get_session()

        # Clear existing data
        clear_database(session)

        # Create data using bulk operations
        customers = create_customers_bulk(session)
        services = create_custom_services_bulk(session)
        purchases = create_purchases_bulk(session)
        payments = create_payments_bulk(session)

        # Calculate end time and elapsed time
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        # Print statistics
        print_statistics(session)

        print("\n" + "=" * 60)
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(
            f"Elapsed time: {elapsed_time:.2f} seconds ({elapsed_time / 60:.2f} minutes)"
        )
        print(
            f"Performance: {N_CUSTOMERS + N_PURCHASES + N_PAYMENTS:,} records in {elapsed_time:.2f}s = {(N_CUSTOMERS + N_PURCHASES + N_PAYMENTS) / elapsed_time:.0f} records/second"
        )
        print("=" * 60)

    except Exception as e:
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        print(
            f"\nError during database population after {elapsed_time:.2f} seconds: {e}"
        )
        if session:
            session.rollback()
        sys.exit(1)
    finally:
        if session:
            close_session(session)


if __name__ == "__main__":
    main()
