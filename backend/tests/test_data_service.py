"""Unit tests for app.services.data_service."""

from app.services.data_service import (
    get_customer_transactions,
    get_product_info,
    get_business_metrics,
    compare_customers,
    compare_products,
)
from app.models import Transaction


class TestGetCustomerTransactions:
    def test_found(self, app_ctx):
        result = get_customer_transactions("109318")
        assert "109318" in result
        assert "2 transaction" in result
        assert "Electronics" in result
        assert "Total spend" in result

    def test_not_found(self, app_ctx):
        result = get_customer_transactions("999999")
        assert "No transactions found" in result
        assert "999999" in result


class TestGetProductInfo:
    def test_aggregated_stats(self, app_ctx):
        rows = Transaction.query.filter_by(product_id="A").all()
        result = get_product_info("A", rows)
        assert "Product A" in result
        assert "Total Qty" in result
        assert "Total Revenue" in result
        assert "Avg Price" in result

    def test_no_rows(self, app_ctx):
        result = get_product_info("Z", [])
        assert "No transactions found" in result


class TestGetBusinessMetrics:
    def test_metrics(self, app_ctx):
        rows = Transaction.query.all()
        result = get_business_metrics(rows)
        assert "Business Metrics" in result
        assert "Total Revenue" in result
        assert "Unique Customers" in result
        assert "Unique Products" in result
        assert "Revenue by Category" in result

    def test_empty(self, app_ctx):
        result = get_business_metrics([])
        assert "No transaction data" in result


class TestCompareCustomers:
    def test_both_exist(self, app_ctx):
        result = compare_customers("109318", "993229")
        assert "109318" in result
        assert "993229" in result
        assert "Comparison" in result

    def test_one_missing(self, app_ctx):
        result = compare_customers("109318", "000000")
        assert "No transactions found" in result
        assert "000000" in result


class TestCompareProducts:
    def test_both_exist(self, app_ctx):
        result = compare_products("A", "B")
        assert "Product A" in result
        assert "Product B" in result

    def test_both_missing(self, app_ctx):
        result = compare_products("X", "Y")
        assert "No transactions found" in result
