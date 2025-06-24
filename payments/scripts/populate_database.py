#!/usr/bin/env python
"""
Database Population Script

This script populates the main database with:
- 100,000 customers
- 20 telecom/mobile/internet services
- 200,000 purchases (using existing customers and services with normal distribution)
- 250,000 payments (using existing customers and purchases)

It clears all existing data before populating.
"""

import os
import sys
import django
import numpy as np
from datetime import timedelta, datetime
from django.utils import timezone

# Add the project root to the Python path
# Now we need to go up two levels: payments/scripts/ -> payments/ -> project_root
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payments_dashboard_mini.settings")
django.setup()

from payments.models import (
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
from payments.factories import (
    CustomerFactory,
    PaymentWithExistingFactory,
    PurchaseWithExistingFactory,
    ServiceFactory,
)

# Constants
N_CUSTOMERS = 2000
N_SERVICES = 20
N_PURCHASES = 2000
N_PAYMENTS = 2000

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
# Using normal distribution to create realistic popularity
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


def clear_database():
    """Clear all existing data from the database tables."""
    print("Clearing existing data...")

    # Delete in reverse order to respect foreign key constraints
    Payment.objects.all().delete()
    Purchase.objects.all().delete()
    Service.objects.all().delete()
    Customer.objects.all().delete()

    print("Database cleared successfully.")


def create_customers(n_customers=N_CUSTOMERS):
    """Create the specified number of customers."""
    print(f"Creating {n_customers} customers...")

    customers = []
    for i in range(n_customers):
        customer = CustomerFactory()
        customers.append(customer)

        if (i + 1) % 1000 == 0:
            print(f"Created {i + 1} customers...")

    print(f"Successfully created {len(customers)} customers.")
    return customers


def create_custom_services():
    """Create custom telecom services with predefined names and realistic pricing."""
    print(f"Creating {len(TELECOM_SERVICES)} custom telecom services...")

    services = []
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
                base_price = np.random.uniform(80, 120)
            elif "500Mbps" in service_name:
                base_price = np.random.uniform(50, 80)
            elif "200Mbps" in service_name:
                base_price = np.random.uniform(40, 60)
            elif "100Mbps" in service_name:
                base_price = np.random.uniform(25, 45)
            elif "50Mbps" in service_name:
                base_price = np.random.uniform(20, 35)
            else:  # 25Mbps
                base_price = np.random.uniform(15, 25)
            is_recurring = True
            billing_cycle = BillingCycle.MONTHLY
        elif "Mobile" in service_name:
            service_type = ServiceType.MOBILE
            # More data = higher prices
            if "Unlimited" in service_name:
                base_price = np.random.uniform(40, 60)
            elif "50GB" in service_name:
                base_price = np.random.uniform(35, 50)
            elif "20GB" in service_name:
                base_price = np.random.uniform(25, 35)
            elif "10GB" in service_name:
                base_price = np.random.uniform(20, 30)
            elif "5GB" in service_name:
                base_price = np.random.uniform(15, 25)
            else:  # Family plans
                base_price = np.random.uniform(30, 45)
            is_recurring = True
            billing_cycle = BillingCycle.MONTHLY
        else:  # TV services
            service_type = ServiceType.TV
            if "Premium" in service_name:
                base_price = np.random.uniform(30, 50)
            elif "Sports" in service_name or "Movie" in service_name:
                base_price = np.random.uniform(20, 35)
            else:  # Basic and Family
                base_price = np.random.uniform(15, 25)
            is_recurring = True
            billing_cycle = BillingCycle.MONTHLY

        service = Service.objects.create(
            name=service_name,
            type=service_type,
            base_price=base_price,
            is_recurring=is_recurring,
            billing_cycle=billing_cycle,
        )
        services.append(service)

        if (i + 1) % 10 == 0:
            print(f"Created {i + 1} services...")

    print(f"Successfully created {len(services)} custom telecom services.")
    return services


def create_purchases_with_popularity(
    n_purchases=N_PURCHASES, customers=None, services=None
):
    """Create purchases using existing customers and services with popularity-based selection."""
    print(
        f"Creating {n_purchases} purchases with popularity-based service selection..."
    )

    if not customers:
        customers = list(Customer.objects.all())
    if not services:
        services = list(Service.objects.all())

    if not customers or not services:
        raise ValueError("No customers or services available for purchase creation")

    purchases = []
    for i in range(n_purchases):
        # Select customer randomly
        customer = np.random.choice(customers)

        # Select service based on popularity weights (normal distribution)
        service = np.random.choice(services, p=SERVICE_POPULARITY_WEIGHTS)

        # Create purchase with existing customer and service
        purchase = PurchaseWithExistingFactory(customer=customer, service=service)
        purchases.append(purchase)

        if (i + 1) % 1000 == 0:
            print(f"Created {i + 1} purchases...")

    print(f"Successfully created {len(purchases)} purchases.")
    return purchases


def create_payments(n_payments=N_PAYMENTS, customers=None, purchases=None):
    """Create payments using existing customers and purchases with amounts matching service base prices."""
    print(f"Creating {n_payments} payments...")

    if not customers:
        customers = list(Customer.objects.all())
    if not purchases:
        purchases = list(Purchase.objects.all())

    if not customers or not purchases:
        raise ValueError("No customers or purchases available for payment creation")

    payments = []
    purchase_customer_payments = 0
    different_customer_payments = 0

    for i in range(n_payments):
        # Randomly select purchase
        purchase = np.random.choice(purchases)

        # 95% chance the payment customer is the same as purchase customer
        # 5% chance it's a random different customer
        if np.random.random() < 0.95:
            # Use the purchase customer (95% of cases)
            customer = purchase.customer
            purchase_customer_payments += 1
        else:
            # Use a random different customer (5% of cases)
            other_customers = [c for c in customers if c != purchase.customer]
            customer = np.random.choice(other_customers)
            different_customer_payments += 1

        # Create payment with amount matching the service base price
        payment = Payment.objects.create(
            customer=customer,
            purchase=purchase,
            amount=purchase.service.base_price,  # Use service base price
            currency=np.random.choice([e.value for e in Currency]),
            payment_method=np.random.choice([e.value for e in PaymentMethod]),
            status=np.random.choice([e.value for e in PaymentStatus]),
            timestamp=timezone.now() - timedelta(days=np.random.randint(1, 365)),
        )
        payments.append(payment)

        if (i + 1) % 1000 == 0:
            print(f"Created {i + 1} payments...")

    print(f"Successfully created {len(payments)} payments.")
    print(
        f"  - Payments by purchase customer: {purchase_customer_payments} ({(purchase_customer_payments / n_payments) * 100:.1f}%)"
    )
    print(
        f"  - Payments by different customer: {different_customer_payments} ({(different_customer_payments / n_payments) * 100:.1f}%)"
    )
    return payments


def print_service_popularity_stats():
    """Print statistics about service popularity."""
    print("\nService Popularity Statistics:")
    print("-" * 50)

    services = list(Service.objects.all())
    for i, service in enumerate(services):
        purchase_count = service.purchases.count()
        popularity_percentage = (purchase_count / Purchase.objects.count()) * 100
        print(
            f"{service.name}: {purchase_count} purchases ({popularity_percentage:.1f}%)"
        )


def verify_payment_amounts():
    """Verify that payment amounts match service base prices and customer relationships."""
    print("\nPayment Verification:")
    print("-" * 50)

    total_payments = Payment.objects.count()
    correct_amounts = 0
    matching_customers = 0

    for payment in Payment.objects.all():
        # Check if amount matches service price
        if (
            abs(payment.amount - payment.purchase.service.base_price) < 0.01
        ):  # Allow for floating point precision
            correct_amounts += 1

        # Check if payment customer matches purchase customer
        if payment.customer == payment.purchase.customer:
            matching_customers += 1

    amount_accuracy = (correct_amounts / total_payments) * 100
    customer_accuracy = (matching_customers / total_payments) * 100

    print(f"Amount Verification:")
    print(
        f"  - Payments with correct amounts: {correct_amounts}/{total_payments} ({amount_accuracy:.1f}%)"
    )
    if amount_accuracy == 100:
        print("  ✅ All payment amounts correctly match service base prices!")
    else:
        print("  ❌ Some payment amounts do not match service base prices")

    print(f"\nCustomer Relationship Verification:")
    print(
        f"  - Payments by purchase customer: {matching_customers}/{total_payments} ({customer_accuracy:.1f}%)"
    )
    print(
        f"  - Payments by different customer: {total_payments - matching_customers}/{total_payments} ({100 - customer_accuracy:.1f}%)"
    )
    if customer_accuracy >= 95:
        print("  ✅ Customer relationship distribution is realistic!")
    else:
        print("  ⚠️  Customer relationship distribution may need adjustment")

    # Show a few examples
    print("\nSample Payment Details:")
    print("-" * 30)
    for payment in Payment.objects.all()[:5]:
        service_name = payment.purchase.service.name
        service_price = payment.purchase.service.base_price
        payment_amount = payment.amount
        purchase_customer = payment.purchase.customer.name
        payment_customer = payment.customer.name
        customer_match = "✅" if payment.customer == payment.purchase.customer else "❌"
        print(
            f"{service_name}: ${payment_amount:.2f} | Purchase: {purchase_customer} | Payment: {payment_customer} {customer_match}"
        )


def main():
    """Main function to populate the database."""
    start_time = datetime.now()
    print("Starting database population...")
    print("=" * 50)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    try:
        # Clear existing data
        clear_database()

        # Create customers
        customers = create_customers()

        # Create custom telecom services
        services = create_custom_services()

        # Create purchases using existing customers and services with popularity
        purchases = create_purchases_with_popularity(
            customers=customers, services=services
        )

        # Create payments using existing customers and purchases
        payments = create_payments(customers=customers, purchases=purchases)

        # Calculate end time and elapsed time
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        # Print final statistics
        print("\n")
        separator_line = "=" * 50
        print(separator_line)
        print("DATABASE POPULATION COMPLETED SUCCESSFULLY!")
        print(separator_line)
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(
            f"Elapsed time: {elapsed_time:.2f} seconds ({elapsed_time / 60:.2f} minutes)"
        )
        print(separator_line)
        print(f"Total customers: {Customer.objects.count()}")
        print(f"Total services: {Service.objects.count()}")
        print(f"Total purchases: {Purchase.objects.count()}")
        print(f"Total payments: {Payment.objects.count()}")
        print(separator_line)

        # Print service popularity statistics
        print_service_popularity_stats()

        # Verify payment amounts
        verify_payment_amounts()

    except Exception as e:
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        print(
            f"\nError during database population after {elapsed_time:.2f} seconds: {e}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
