#!/usr/bin/env python
"""
Test script to verify Django ORM and SQLAlchemy queries work correctly.
"""

import os
import sys
import django

# Add the project root to the Python path (go up two levels from payments/tests/)
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payments_dashboard_mini.settings")
django.setup()

from payments.models import Payment, Service, ServiceType, PaymentStatus, PaymentMethod
from payments.db import get_session, close_session
from payments.sqlalchemy_models import (
    Payment as SAPayment,
    Service as SAService,
    Purchase as SAPurchase,
    Customer as SACustomer,
)
from sqlalchemy import func, case


def test_django_orm():
    """Test Django ORM query."""
    print("Testing Django ORM query...")

    recent_payments = Payment.objects.select_related(
        "customer", "purchase__service"
    ).order_by("-timestamp")[:5]

    print(f"Found {len(recent_payments)} recent payments:")
    for payment in recent_payments:
        print(
            f"  - {payment.customer.name} paid ${payment.amount:.2f} for {payment.purchase.service.name}"
        )

    print("✅ Django ORM query successful!\n")


def test_sqlalchemy():
    """Test SQLAlchemy queries."""
    print("Testing SQLAlchemy queries...")

    session = get_session()
    try:
        # Test service statistics query
        service_stats = (
            session.query(
                SAService.type,
                func.count(SAPayment.id).label("total_payments"),
                func.sum(SAPayment.amount).label("total_amount"),
                func.avg(SAPayment.amount).label("avg_amount"),
            )
            .join(SAPurchase, SAPayment.purchase_id == SAPurchase.id)
            .join(SAService, SAPurchase.service_id == SAService.id)
            .group_by(SAService.type)
            .limit(3)
            .all()
        )

        print(f"Found {len(service_stats)} service type statistics:")
        for stat in service_stats:
            print(
                f"  - Service Type {stat.type}: {stat.total_payments} payments, ${stat.total_amount:.2f} total"
            )

        # Test top customers query
        top_customers = (
            session.query(
                SACustomer.name,
                func.sum(SAPayment.amount).label("total_spent"),
                func.count(SAPayment.id).label("payment_count"),
            )
            .join(SACustomer, SAPayment.customer_id == SACustomer.id)
            .group_by(SACustomer.name)
            .order_by(func.sum(SAPayment.amount).desc())
            .limit(3)
            .all()
        )

        print(f"Found {len(top_customers)} top customers:")
        for customer in top_customers:
            print(
                f"  - {customer.name}: ${customer.total_spent:.2f} total, {customer.payment_count} payments"
            )

        print("✅ SQLAlchemy queries successful!\n")

    finally:
        close_session(session)


def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing Django ORM and SQLAlchemy Queries")
    print("=" * 50)

    try:
        test_django_orm()
        test_sqlalchemy()
        print("🎉 All tests passed! The dashboard should work correctly.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
