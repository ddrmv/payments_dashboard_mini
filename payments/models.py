from django.db import models
from enum import IntEnum
from django.utils import timezone


class AccountStatus(IntEnum):
    ACTIVE = 1
    SUSPENDED = 2
    TERMINATED = 3


class ServiceType(IntEnum):
    INTERNET = 1
    MOBILE = 2
    ONE_OFF = 3
    TV = 4


class BillingCycle(IntEnum):
    MONTHLY = 1
    YEARLY = 2


class PurchaseStatus(IntEnum):
    ACTIVE = 1
    CANCELED = 2
    EXPIRED = 3
    AWAITING_ACTIVATION = 4


class PaymentMethod(IntEnum):
    CREDIT_CARD = 1
    BANK_TRANSFER = 2
    MOBILE_PAYMENT = 3
    CASH_PAYMENT = 4


class PaymentStatus(IntEnum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    REFUNDED = 4


class Currency(IntEnum):
    EUR = 1
    BGN = 2
    USD = 3
    GBP = 4


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    account_status = models.IntegerField(
        choices=[(e.value, e.name) for e in AccountStatus], default=AccountStatus.ACTIVE
    )

    class Meta:
        db_table = "customers"


class Service(models.Model):
    name = models.CharField(max_length=100)
    type = models.IntegerField(choices=[(e.value, e.name) for e in ServiceType])
    base_price = models.FloatField()
    is_recurring = models.BooleanField()
    billing_cycle = models.IntegerField(
        choices=[(e.value, e.name) for e in BillingCycle], null=True, blank=True
    )

    class Meta:
        db_table = "services"


class Purchase(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="purchases"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="purchases"
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(
        choices=[(e.value, e.name) for e in PurchaseStatus],
        default=PurchaseStatus.ACTIVE,
    )

    class Meta:
        db_table = "purchases"


class Payment(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="payments"
    )
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.FloatField()
    currency = models.IntegerField(
        choices=[(e.value, e.name) for e in Currency], default=Currency.BGN
    )
    payment_method = models.IntegerField(
        choices=[(e.value, e.name) for e in PaymentMethod]
    )
    status = models.IntegerField(
        choices=[(e.value, e.name) for e in PaymentStatus],
        default=PaymentStatus.PENDING,
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "payments"
