from django.shortcuts import render
from django.db.models import Count, Avg, Sum
from payments.models import Payment, Service, ServiceType, PaymentStatus, PaymentMethod
from payments.db import get_session, close_session
from payments.sqlalchemy_models import (
    Payment as SAPayment,
    Service as SAService,
    Purchase as SAPurchase,
    Customer as SACustomer,
)
from sqlalchemy import func, case, and_
from sqlalchemy.orm import joinedload


def dashboard_view(request):
    """
    Dashboard view demonstrating both Django ORM and SQLAlchemy queries.

    Django ORM: Simple query for last 10 payments
    SQLAlchemy: Complex query for payment statistics by service type
    """

    # Django ORM Query - Simple: Get last 10 payments with related data
    recent_payments = Payment.objects.select_related(
        "customer", "purchase__service"
    ).order_by("-timestamp")[:5]

    # SQLAlchemy Query - Complex: Payment statistics by service type with advanced aggregations
    session = get_session()
    try:
        # Complex query: Payment statistics by service type
        # This includes:
        # - Total payments and amounts by service type
        # - Average payment amount by service type
        # - Success rate by service type
        # - Payment method distribution
        service_stats = (
            session.query(
                SAService.type,
                func.count(SAPayment.id).label("total_payments"),
                func.sum(SAPayment.amount).label("total_amount"),
                func.avg(SAPayment.amount).label("avg_amount"),
                func.sum(
                    case(
                        (SAPayment.status == PaymentStatus.COMPLETED.value, 1), else_=0
                    )
                ).label("successful_payments"),
                func.count(
                    case(
                        (SAPayment.payment_method == 1, 1),  # Credit Card
                        else_=None,
                    )
                ).label("credit_card_payments"),
                func.count(
                    case(
                        (SAPayment.payment_method == 2, 1),  # Bank Transfer
                        else_=None,
                    )
                ).label("bank_transfer_payments"),
                func.count(
                    case(
                        (SAPayment.payment_method == 3, 1),  # Mobile Payment
                        else_=None,
                    )
                ).label("mobile_payments"),
            )
            .join(SAPurchase, SAPayment.purchase_id == SAPurchase.id)
            .join(SAService, SAPurchase.service_id == SAService.id)
            .group_by(SAService.type)
            .all()
        )

        # Additional complex query: Top 5 customers by total payment amount
        top_customers = (
            session.query(
                SACustomer.name,
                func.sum(SAPayment.amount).label("total_spent"),
                func.count(SAPayment.id).label("payment_count"),
                func.avg(SAPayment.amount).label("avg_payment"),
            )
            .join(SACustomer, SAPayment.customer_id == SACustomer.id)
            .group_by(SACustomer.name)
            .order_by(func.sum(SAPayment.amount).desc())
            .limit(5)
            .all()
        )

    finally:
        close_session(session)

    # Prepare context data
    context = {
        "recent_payments": recent_payments,
        "service_stats": service_stats,
        "top_customers": top_customers,
        "service_types": {e.value: e.name for e in ServiceType},
        "payment_statuses": {e.value: e.name for e in PaymentStatus},
        "payment_methods": {e.value: e.name for e in PaymentMethod},
    }

    return render(request, "payments/dashboard.html", context)
