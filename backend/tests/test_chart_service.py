"""Unit tests for app.services.chart_service."""

from datetime import datetime
from app.models import Transaction
from app.services.chart_service import (
    build_product_charts,
    build_business_charts,
    build_comparison_charts,
)


def _make_row(**overrides):
    """Create a Transaction instance with sensible defaults."""
    defaults = {
        "customer_id": "100", "product_id": "A", "quantity": 1,
        "price": 10.0, "transaction_date": datetime(2024, 1, 1),
        "payment_method": "Cash", "store_location": "Test St",
        "product_category": "Electronics", "discount_applied": 0.0,
        "total_amount": 10.0,
    }
    defaults.update(overrides)
    return Transaction(**defaults)


class TestBuildProductCharts:
    def test_structure(self):
        rows = [_make_row(), _make_row(payment_method="PayPal")]
        charts = build_product_charts("A", rows)
        assert len(charts) == 2
        assert charts[0]["type"] == "bar"
        assert charts[1]["type"] == "pie"
        assert all("data" in c for c in charts)

    def test_empty(self):
        assert build_product_charts("A", []) is None


class TestBuildBusinessCharts:
    def test_structure(self):
        rows = [
            _make_row(product_category="Books", total_amount=20),
            _make_row(product_category="Electronics", total_amount=30),
        ]
        charts = build_business_charts(rows)
        assert len(charts) == 2
        assert charts[0]["type"] == "bar"
        assert charts[0]["title"] == "Revenue by Category"
        assert charts[1]["type"] == "pie"
        assert charts[1]["title"] == "Revenue by Payment Method"

    def test_empty(self):
        assert build_business_charts([]) is None


class TestBuildComparisonCharts:
    def test_customer_comparison(self):
        r1 = [_make_row(customer_id="1")]
        r2 = [_make_row(customer_id="2")]
        charts = build_comparison_charts("customer", "1", "2", r1, r2)
        assert len(charts) >= 1
        assert charts[0]["type"] == "grouped_bar"

    def test_product_comparison(self):
        r1 = [_make_row(product_id="A")]
        r2 = [_make_row(product_id="B")]
        charts = build_comparison_charts("product", "A", "B", r1, r2)
        assert len(charts) >= 1
        assert charts[0]["type"] == "grouped_bar"
