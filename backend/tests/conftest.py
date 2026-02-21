"""Shared fixtures for backend tests."""

import pytest
from datetime import datetime

from app import create_app
from app.extensions import db as _db
from app.models import Transaction


@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing with in-memory SQLite."""
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="session")
def seeded_app(app):
    """App with sample data already inserted (session-scoped for speed)."""
    with app.app_context():
        _seed_sample_data()
    return app


@pytest.fixture()
def client(seeded_app):
    """Flask test client with seeded data."""
    return seeded_app.test_client()


@pytest.fixture()
def app_ctx(seeded_app):
    """Push an application context for service-level tests."""
    with seeded_app.app_context():
        yield


# --------------- sample data ---------------

SAMPLE_ROWS = [
    # Customer 109318 — 2 transactions
    {
        "customer_id": "109318", "product_id": "A", "quantity": 3,
        "price": 25.00, "transaction_date": datetime(2024, 1, 15, 10, 30),
        "payment_method": "Credit Card", "store_location": "123 Main St, New York",
        "product_category": "Electronics", "discount_applied": 5.0,
        "total_amount": 71.25,
    },
    {
        "customer_id": "109318", "product_id": "B", "quantity": 1,
        "price": 15.00, "transaction_date": datetime(2024, 2, 20, 14, 0),
        "payment_method": "Cash", "store_location": "456 Oak Ave, Chicago",
        "product_category": "Books", "discount_applied": 0.0,
        "total_amount": 15.00,
    },
    # Customer 993229 — 2 transactions
    {
        "customer_id": "993229", "product_id": "A", "quantity": 2,
        "price": 25.00, "transaction_date": datetime(2024, 3, 10, 9, 0),
        "payment_method": "PayPal", "store_location": "789 Elm Rd, Houston",
        "product_category": "Electronics", "discount_applied": 10.0,
        "total_amount": 45.00,
    },
    {
        "customer_id": "993229", "product_id": "C", "quantity": 5,
        "price": 8.00, "transaction_date": datetime(2024, 4, 5, 16, 45),
        "payment_method": "Debit Card", "store_location": "321 Pine Blvd, Seattle",
        "product_category": "Clothing", "discount_applied": 15.0,
        "total_amount": 34.00,
    },
    # Extra rows for product B and D
    {
        "customer_id": "500000", "product_id": "B", "quantity": 4,
        "price": 15.00, "transaction_date": datetime(2024, 5, 1, 11, 0),
        "payment_method": "Credit Card", "store_location": "123 Main St, New York",
        "product_category": "Books", "discount_applied": 5.0,
        "total_amount": 57.00,
    },
    {
        "customer_id": "500000", "product_id": "D", "quantity": 1,
        "price": 120.00, "transaction_date": datetime(2024, 6, 15, 8, 0),
        "payment_method": "PayPal", "store_location": "456 Oak Ave, Chicago",
        "product_category": "Home Decor", "discount_applied": 0.0,
        "total_amount": 120.00,
    },
]


def _seed_sample_data():
    """Insert sample transactions into the test database."""
    for row in SAMPLE_ROWS:
        _db.session.add(Transaction(**row))
    _db.session.commit()
