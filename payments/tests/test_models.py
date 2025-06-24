import pytest
from payments.tests.factories import (
    CustomerFactory,
    ServiceFactory,
    PurchaseFactory,
    PaymentFactory,
    generate_bulk_data,
)
from payments.models import (
    Customer,
    Payment,
    AccountStatus,
    Service,
    Purchase,
    ServiceType,
    BillingCycle,
    PurchaseStatus,
)


@pytest.mark.django_db
def test_customer_creation():
    customer = CustomerFactory()
    assert Customer.objects.count() == 1
    assert customer.name and customer.email
    assert customer.account_status in [e.value for e in AccountStatus]


@pytest.mark.django_db
def test_bulk_data_population():
    # Clean up any existing data first
    Customer.objects.all().delete()
    Service.objects.all().delete()
    Purchase.objects.all().delete()
    Payment.objects.all().delete()

    generate_bulk_data(n_customers=5, n_services=3, n_purchases=10, n_payments=20)
    assert Customer.objects.count() == 5
    assert Payment.objects.count() == 20


@pytest.mark.django_db
def test_payment_amount():
    payment = PaymentFactory(amount=150.0)
    assert payment.amount == 150.0
    assert Payment.objects.filter(amount__gte=100).count() == 1


# Service Model Tests
@pytest.mark.django_db
def test_service_creation():
    service = ServiceFactory()
    assert Service.objects.count() == 1
    assert service.name
    assert service.type in [e.value for e in ServiceType]
    assert service.base_price > 0
    assert isinstance(service.is_recurring, bool)


@pytest.mark.django_db
def test_service_type_validation():
    service = ServiceFactory(type=ServiceType.INTERNET)
    assert service.type == ServiceType.INTERNET
    assert service.type == 1


@pytest.mark.django_db
def test_service_billing_cycle():
    # Test recurring service with billing cycle
    service = ServiceFactory(is_recurring=True, billing_cycle=BillingCycle.MONTHLY)
    assert service.is_recurring is True
    assert service.billing_cycle == BillingCycle.MONTHLY

    # Test non-recurring service (billing_cycle can be null)
    service = ServiceFactory(is_recurring=False, billing_cycle=None)
    assert service.is_recurring is False
    assert service.billing_cycle is None


@pytest.mark.django_db
def test_service_base_price():
    service = ServiceFactory(base_price=99.99)
    assert service.base_price == 99.99
    assert Service.objects.filter(base_price__gte=50).count() == 1


@pytest.mark.django_db
def test_service_relationships():
    service = ServiceFactory()
    # Test that service can have purchases
    purchase = PurchaseFactory(service=service)
    assert purchase.service == service
    assert service.purchases.count() == 1


# Purchase Model Tests
@pytest.mark.django_db
def test_purchase_creation():
    purchase = PurchaseFactory()
    assert Purchase.objects.count() == 1
    assert purchase.customer is not None
    assert purchase.service is not None
    assert purchase.start_date is not None
    assert purchase.status in [e.value for e in PurchaseStatus]


@pytest.mark.django_db
def test_purchase_status_validation():
    purchase = PurchaseFactory(status=PurchaseStatus.ACTIVE)
    assert purchase.status == PurchaseStatus.ACTIVE
    assert purchase.status == 1


@pytest.mark.django_db
def test_purchase_dates():
    from django.utils import timezone
    from datetime import timedelta

    # Test purchase with end date
    start_date = timezone.now()
    end_date = start_date + timedelta(days=30)
    purchase = PurchaseFactory(start_date=start_date, end_date=end_date)
    assert purchase.start_date == start_date
    assert purchase.end_date == end_date

    # Test purchase without end date
    purchase = PurchaseFactory(end_date=None)
    assert purchase.start_date is not None
    assert purchase.end_date is None


@pytest.mark.django_db
def test_purchase_relationships():
    customer = CustomerFactory()
    service = ServiceFactory()
    purchase = PurchaseFactory(customer=customer, service=service)

    # Test customer relationship
    assert purchase.customer == customer
    assert customer.purchases.count() == 1

    # Test service relationship
    assert purchase.service == service
    assert service.purchases.count() == 1


@pytest.mark.django_db
def test_purchase_payments_relationship():
    purchase = PurchaseFactory()
    payment1 = PaymentFactory(purchase=purchase)
    payment2 = PaymentFactory(purchase=purchase)

    assert purchase.payments.count() == 2
    assert payment1 in purchase.payments.all()
    assert payment2 in purchase.payments.all()


@pytest.mark.django_db
def test_purchase_end_date_logic():
    # Test that recurring services get end dates
    recurring_service = ServiceFactory(is_recurring=True)
    purchase = PurchaseFactory(service=recurring_service)

    # The factory should automatically set end_date for recurring services
    if purchase.end_date is not None:
        assert purchase.end_date > purchase.start_date

    # Test that non-recurring services can have null end dates
    non_recurring_service = ServiceFactory(is_recurring=False)
    purchase = PurchaseFactory(service=non_recurring_service, end_date=None)
    assert purchase.end_date is None


@pytest.mark.django_db
def test_purchase_cascade_deletion():
    customer = CustomerFactory()
    service = ServiceFactory()
    purchase = PurchaseFactory(customer=customer, service=service)
    payment = PaymentFactory(purchase=purchase)

    # Delete the purchase
    purchase_id = purchase.id
    purchase.delete()

    # Verify purchase is deleted
    assert Purchase.objects.filter(id=purchase_id).count() == 0
    # Verify related payment is also deleted (CASCADE)
    assert Payment.objects.filter(id=payment.id).count() == 0
    # Verify customer and service still exist
    assert Customer.objects.filter(id=customer.id).count() == 1
    assert Service.objects.filter(id=service.id).count() == 1


@pytest.mark.django_db
def test_service_cascade_deletion():
    service = ServiceFactory()
    purchase = PurchaseFactory(service=service)
    payment = PaymentFactory(purchase=purchase)

    # Delete the service
    service_id = service.id
    service.delete()

    # Verify service is deleted
    assert Service.objects.filter(id=service_id).count() == 0
    # Verify related purchase is also deleted (CASCADE)
    assert Purchase.objects.filter(id=purchase.id).count() == 0
    # Verify related payment is also deleted (CASCADE)
    assert Payment.objects.filter(id=payment.id).count() == 0


@pytest.mark.django_db
def test_customer_cascade_deletion():
    customer = CustomerFactory()
    purchase = PurchaseFactory(customer=customer)
    payment = PaymentFactory(customer=customer, purchase=purchase)

    # Delete the customer
    customer_id = customer.id
    customer.delete()

    # Verify customer is deleted
    assert Customer.objects.filter(id=customer_id).count() == 0
    # Verify related purchase is also deleted (CASCADE)
    assert Purchase.objects.filter(id=purchase.id).count() == 0
    # Verify related payment is also deleted (CASCADE)
    assert Payment.objects.filter(id=payment.id).count() == 0
