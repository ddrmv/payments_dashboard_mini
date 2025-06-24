"""
SQLAlchemy models for the payments dashboard.

These models mirror the Django models but are optimized for SQLAlchemy operations,
particularly for bulk inserts and complex queries.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
import enum

Base = declarative_base()


class AccountStatus(enum.Enum):
    ACTIVE = 1
    SUSPENDED = 2
    TERMINATED = 3


class ServiceType(enum.Enum):
    INTERNET = 1
    MOBILE = 2
    ONE_OFF = 3
    TV = 4


class BillingCycle(enum.Enum):
    MONTHLY = 1
    YEARLY = 2


class PurchaseStatus(enum.Enum):
    ACTIVE = 1
    CANCELED = 2
    EXPIRED = 3
    AWAITING_ACTIVATION = 4


class PaymentMethod(enum.Enum):
    CREDIT_CARD = 1
    BANK_TRANSFER = 2
    MOBILE_PAYMENT = 3
    CASH_PAYMENT = 4


class PaymentStatus(enum.Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    REFUNDED = 4


class Currency(enum.Enum):
    EUR = 1
    BGN = 2
    USD = 3
    GBP = 4


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    account_status = Column(Integer, default=AccountStatus.ACTIVE.value)

    # Relationships
    purchases = relationship("Purchase", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(Integer, nullable=False)
    base_price = Column(Float, nullable=False)
    is_recurring = Column(Boolean, default=True)
    billing_cycle = Column(Integer, nullable=True)

    # Relationships
    purchases = relationship("Purchase", back_populates="service")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    status = Column(Integer, default=PurchaseStatus.ACTIVE.value)

    # Relationships
    customer = relationship("Customer", back_populates="purchases")
    service = relationship("Service", back_populates="purchases")
    payments = relationship("Payment", back_populates="purchase")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(Integer, default=Currency.BGN.value)
    payment_method = Column(Integer, nullable=False)
    status = Column(Integer, default=PaymentStatus.PENDING.value)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="payments")
    purchase = relationship("Purchase", back_populates="payments")
