"""Data access service — queries the PostgreSQL transactions table."""

import json
from app.extensions import db
from app.models import Transaction


def get_customer_transactions(customer_id: str, limit: int = 20) -> str:
    """Get recent transactions for a customer, formatted as a string for the LLM."""
    rows = (
        Transaction.query
        .filter_by(customer_id=customer_id)
        .order_by(Transaction.transaction_date.desc())
        .limit(limit)
        .all()
    )
    if not rows:
        return f"No transactions found for customer {customer_id}."

    lines = [f"Found {len(rows)} transaction(s) for customer {customer_id}:\n"]
    total_spend = 0
    for r in rows:
        lines.append(
            f"- {r.transaction_date.strftime('%Y-%m-%d')} | "
            f"Product {r.product_id} ({r.product_category}) | "
            f"Qty {r.quantity} × ${r.price:.2f} | "
            f"Discount {r.discount_applied:.1f}% | "
            f"Total ${r.total_amount:.2f} | "
            f"{r.payment_method} | {r.store_location}"
        )
        total_spend += r.total_amount

    lines.append(f"\nTotal spend: ${total_spend:.2f}")
    return "\n".join(lines)


def get_product_info(product_id: str) -> str:
    """Get aggregated info about a product ID."""
    rows = Transaction.query.filter_by(product_id=product_id).all()

    if not rows:
        return f"No transactions found for product {product_id}."

    total_qty = sum(r.quantity for r in rows)
    total_revenue = sum(r.total_amount for r in rows)
    avg_price = sum(r.price for r in rows) / len(rows)
    avg_discount = sum(r.discount_applied for r in rows) / len(rows)
    stores = sorted(set(r.store_location for r in rows))
    categories = sorted(set(r.product_category for r in rows))
    payment_methods = {}
    for r in rows:
        payment_methods[r.payment_method] = payment_methods.get(r.payment_method, 0) + 1

    lines = [
        f"Product {product_id} summary ({len(rows)} transactions):",
        f"- Categories: {', '.join(categories)}",
        f"- Total quantity sold: {total_qty}",
        f"- Total revenue: ${total_revenue:.2f}",
        f"- Average price: ${avg_price:.2f}",
        f"- Average discount: {avg_discount:.1f}%",
        f"- Payment methods: {json.dumps(payment_methods)}",
        f"- Sold in {len(stores)} store location(s)",
    ]

    # Show first 10 stores
    for s in stores[:10]:
        lines.append(f"  • {s}")
    if len(stores) > 10:
        lines.append(f"  ... and {len(stores) - 10} more")

    return "\n".join(lines)


def get_business_metrics() -> str:
    """Get general business metrics."""
    rows = Transaction.query.all()

    if not rows:
        return "No transaction data available."

    total_revenue = sum(r.total_amount for r in rows)
    total_transactions = len(rows)
    avg_transaction = total_revenue / total_transactions

    # Revenue by category
    by_category = {}
    for r in rows:
        cat = r.product_category
        by_category[cat] = by_category.get(cat, 0) + r.total_amount

    # Revenue by payment method
    by_payment = {}
    for r in rows:
        pm = r.payment_method
        by_payment[pm] = by_payment.get(pm, 0) + r.total_amount

    # Unique counts
    unique_customers = len(set(r.customer_id for r in rows))
    unique_products = len(set(r.product_id for r in rows))

    lines = [
        f"Business Metrics Overview ({total_transactions} total transactions):",
        f"- Total revenue: ${total_revenue:,.2f}",
        f"- Average transaction value: ${avg_transaction:.2f}",
        f"- Unique customers: {unique_customers}",
        f"- Unique product IDs: {unique_products}",
        "\nRevenue by category:",
    ]
    for cat, rev in sorted(by_category.items(), key=lambda x: -x[1]):
        lines.append(f"  • {cat}: ${rev:,.2f}")

    lines.append("\nRevenue by payment method:")
    for pm, rev in sorted(by_payment.items(), key=lambda x: -x[1]):
        lines.append(f"  • {pm}: ${rev:,.2f}")

    return "\n".join(lines)


def compare_customers(id1: str, id2: str) -> str:
    """Compare two customers side by side."""
    def _stats(cid):
        rows = Transaction.query.filter_by(customer_id=cid).all()
        if not rows:
            return None
        total_spend = sum(r.total_amount for r in rows)
        avg_spend = total_spend / len(rows)
        categories = {}
        for r in rows:
            categories[r.product_category] = categories.get(r.product_category, 0) + r.total_amount
        payment_methods = {}
        for r in rows:
            payment_methods[r.payment_method] = payment_methods.get(r.payment_method, 0) + 1
        return {
            "transactions": len(rows),
            "total_spend": total_spend,
            "avg_spend": avg_spend,
            "categories": categories,
            "payment_methods": payment_methods,
        }

    s1 = _stats(id1)
    s2 = _stats(id2)

    if not s1 and not s2:
        return f"No transactions found for either customer {id1} or customer {id2}."
    if not s1:
        return f"No transactions found for customer {id1}. Customer {id2} has data."
    if not s2:
        return f"Customer {id1} has data. No transactions found for customer {id2}."

    lines = [
        f"Comparison: Customer {id1} vs Customer {id2}\n",
        f"{'Metric':<25} {'Customer ' + id1:<20} {'Customer ' + id2:<20}",
        f"{'-'*65}",
        f"{'Transactions':<25} {s1['transactions']:<20} {s2['transactions']:<20}",
        f"{'Total Spend':<25} ${s1['total_spend']:<19.2f} ${s2['total_spend']:<19.2f}",
        f"{'Avg per Transaction':<25} ${s1['avg_spend']:<19.2f} ${s2['avg_spend']:<19.2f}",
        f"\nSpending by category:",
    ]
    all_cats = sorted(set(list(s1["categories"]) + list(s2["categories"])))
    for cat in all_cats:
        v1 = s1["categories"].get(cat, 0)
        v2 = s2["categories"].get(cat, 0)
        lines.append(f"  {cat:<23} ${v1:<19.2f} ${v2:<19.2f}")

    lines.append(f"\nPayment methods:")
    all_pm = sorted(set(list(s1["payment_methods"]) + list(s2["payment_methods"])))
    for pm in all_pm:
        v1 = s1["payment_methods"].get(pm, 0)
        v2 = s2["payment_methods"].get(pm, 0)
        lines.append(f"  {pm:<23} {v1:<20} {v2:<20}")

    return "\n".join(lines)


def compare_products(id1: str, id2: str) -> str:
    """Compare two products side by side."""
    def _stats(pid):
        rows = Transaction.query.filter_by(product_id=pid).all()
        if not rows:
            return None
        total_qty = sum(r.quantity for r in rows)
        total_rev = sum(r.total_amount for r in rows)
        avg_price = sum(r.price for r in rows) / len(rows)
        avg_disc = sum(r.discount_applied for r in rows) / len(rows)
        stores = len(set(r.store_location for r in rows))
        return {
            "transactions": len(rows),
            "total_qty": total_qty,
            "total_revenue": total_rev,
            "avg_price": avg_price,
            "avg_discount": avg_disc,
            "store_count": stores,
        }

    s1 = _stats(id1)
    s2 = _stats(id2)

    if not s1 and not s2:
        return f"No transactions found for either product {id1} or product {id2}."
    if not s1:
        return f"No transactions found for product {id1}. Product {id2} has data."
    if not s2:
        return f"Product {id1} has data. No transactions found for product {id2}."

    lines = [
        f"Comparison: Product {id1} vs Product {id2}\n",
        f"{'Metric':<25} {'Product ' + id1:<20} {'Product ' + id2:<20}",
        f"{'-'*65}",
        f"{'Transactions':<25} {s1['transactions']:<20} {s2['transactions']:<20}",
        f"{'Total Qty Sold':<25} {s1['total_qty']:<20} {s2['total_qty']:<20}",
        f"{'Total Revenue':<25} ${s1['total_revenue']:<19.2f} ${s2['total_revenue']:<19.2f}",
        f"{'Avg Price':<25} ${s1['avg_price']:<19.2f} ${s2['avg_price']:<19.2f}",
        f"{'Avg Discount %':<25} {s1['avg_discount']:<19.1f}% {s2['avg_discount']:<19.1f}%",
        f"{'Store Locations':<25} {s1['store_count']:<20} {s2['store_count']:<20}",
    ]

    return "\n".join(lines)
