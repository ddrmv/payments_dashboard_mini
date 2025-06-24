import factory
import numpy as np
import pandas as pd
from datetime import timedelta
from django.utils import timezone
from factory.django import DjangoModelFactory

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


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer

    name = factory.Faker("name")
    email = factory.Faker("email")
    account_status = factory.Iterator([e.value for e in AccountStatus])


class ServiceFactory(DjangoModelFactory):
    class Meta:
        model = Service

    name = factory.Faker("word")
    type = factory.Iterator([e.value for e in ServiceType])
    base_price = factory.Faker("pyfloat", positive=True, max_value=100)
    is_recurring = factory.Faker("pybool")
    billing_cycle = factory.Iterator([e.value for e in BillingCycle], cycle=True)


class PurchaseFactory(DjangoModelFactory):
    class Meta:
        model = Purchase

    customer = factory.SubFactory(CustomerFactory)
    service = factory.SubFactory(ServiceFactory)
    start_date = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=np.random.randint(1, 365))
    )
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=30) if o.service.is_recurring else None
    )
    status = factory.Iterator([e.value for e in PurchaseStatus])


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    customer = factory.SubFactory(CustomerFactory)
    purchase = factory.SubFactory(PurchaseFactory)
    amount = factory.Faker("pyfloat", positive=True, max_value=200)
    currency = factory.Iterator([e.value for e in Currency])
    payment_method = factory.Iterator([e.value for e in PaymentMethod])
    status = factory.Iterator([e.value for e in PaymentStatus])
    timestamp = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=np.random.randint(1, 365))
    )


# Factories for bulk data generation that don't create new customers/services
class PurchaseWithExistingFactory(DjangoModelFactory):
    class Meta:
        model = Purchase

    start_date = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=np.random.randint(1, 365))
    )
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=30) if o.service.is_recurring else None
    )
    status = factory.Iterator([e.value for e in PurchaseStatus])


class PaymentWithExistingFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    amount = factory.Faker("pyfloat", positive=True, max_value=200)
    currency = factory.Iterator([e.value for e in Currency])
    payment_method = factory.Iterator([e.value for e in PaymentMethod])
    status = factory.Iterator([e.value for e in PaymentStatus])
    timestamp = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=np.random.randint(1, 365))
    )


def generate_bulk_data(n_customers=10, n_services=5, n_purchases=20, n_payments=50):
    # Generate data with pandas
    customers = [CustomerFactory() for _ in range(n_customers)]
    services = [ServiceFactory() for _ in range(n_services)]
    purchases_data = pd.DataFrame(
        {
            "customer_id": np.random.choice([c.id for c in customers], n_purchases),
            "service_id": np.random.choice([s.id for s in services], n_purchases),
            "start_date": [
                timezone.now() - timedelta(days=np.random.randint(1, 365))
                for _ in range(n_purchases)
            ],
            "status": np.random.choice([e.value for e in PurchaseStatus], n_purchases),
        }
    )
    purchases_data["end_date"] = purchases_data.apply(
        lambda row: row["start_date"] + timedelta(days=30)
        if Service.objects.get(id=row["service_id"]).is_recurring
        else None,
        axis=1,
    )
    purchases = [
        PurchaseWithExistingFactory(
            customer_id=row["customer_id"],
            service_id=row["service_id"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            status=row["status"],
        )
        for _, row in purchases_data.iterrows()
    ]
    payments_data = pd.DataFrame(
        {
            "customer_id": np.random.choice([c.id for c in customers], n_payments),
            "purchase_id": np.random.choice([p.id for p in purchases], n_payments),
            "amount": np.random.uniform(10, 200, n_payments),
            "currency": np.random.choice([e.value for e in Currency], n_payments),
            "payment_method": np.random.choice(
                [e.value for e in PaymentMethod], n_payments
            ),
            "status": np.random.choice([e.value for e in PaymentStatus], n_payments),
            "timestamp": [
                timezone.now() - timedelta(days=np.random.randint(1, 365))
                for _ in range(n_payments)
            ],
        }
    )
    for _, row in payments_data.iterrows():
        PaymentWithExistingFactory(
            customer_id=row["customer_id"],
            purchase_id=row["purchase_id"],
            amount=row["amount"],
            currency=row["currency"],
            payment_method=row["payment_method"],
            status=row["status"],
            timestamp=row["timestamp"],
        )
