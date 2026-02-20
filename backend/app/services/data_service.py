"""Data access service — queries the PostgreSQL transactions table."""

import json
from app.extensions import db
from app.models import Transaction


def _fmt(val):
    """Format a dollar amount."""
    return f"${val:,.2f}"


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
    """Get aggregated info about a product ID with calculation breakdowns."""
    rows = Transaction.query.filter_by(product_id=product_id).all()

    if not rows:
        return f"No transactions found for product {product_id}."

    n = len(rows)
    prices = [r.price for r in rows]
    amounts = [r.total_amount for r in rows]
    quantities = [r.quantity for r in rows]
    discounts = [r.discount_applied for r in rows]
    stores = sorted(set(r.store_location for r in rows))
    categories = sorted(set(r.product_category for r in rows))

    total_qty = sum(quantities)
    total_revenue = sum(amounts)
    sum_prices = sum(prices)
    avg_price = sum_prices / n
    sum_discounts = sum(discounts)
    avg_discount = sum_discounts / n

    payment_methods = {}
    for r in rows:
        payment_methods[r.payment_method] = payment_methods.get(r.payment_method, 0) + 1

    lines = [
        f"Product {product_id} — {n} transactions",
        f"═══════════════════════════════════════",
        f"",
        f"Categories: {', '.join(categories)}",
        f"",
        f"[Calculation Breakdown]",
        f"",
        f"Total Qty Sold = sum of all quantities",
    ]

    # Show sample quantities for breakdown (up to 8 values)
    if n <= 8:
        qty_str = " + ".join(str(q) for q in quantities)
        lines.append(f"  = {qty_str}")
    else:
        sample = quantities[:5]
        qty_str = " + ".join(str(q) for q in sample)
        lines.append(f"  = {qty_str} + ... ({n - 5} more values)")
    lines.append(f"  = {total_qty}")

    lines.append(f"")
    lines.append(f"Total Revenue = sum of all transaction amounts")
    if n <= 8:
        amt_str = " + ".join(f"${a:.2f}" for a in amounts)
        lines.append(f"  = {amt_str}")
    else:
        sample = amounts[:5]
        amt_str = " + ".join(f"${a:.2f}" for a in sample)
        lines.append(f"  = {amt_str} + ... ({n - 5} more)")
    lines.append(f"  = {_fmt(total_revenue)}")

    lines.append(f"")
    lines.append(f"Avg Price = sum(all prices) / count(transactions)")
    lines.append(f"  = {_fmt(sum_prices)} / {n}")
    lines.append(f"  = {_fmt(avg_price)}")

    lines.append(f"")
    lines.append(f"Avg Discount = sum(all discounts) / count(transactions)")
    lines.append(f"  = {sum_discounts:.2f} / {n}")
    lines.append(f"  = {avg_discount:.1f}%")

    lines.append(f"")
    lines.append(f"Payment Methods: {json.dumps(payment_methods)}")
    lines.append(f"Store Locations: {len(stores)}")

    return "\n".join(lines)


def get_business_metrics() -> str:
    """Get general business metrics with calculation breakdowns."""
    rows = Transaction.query.all()

    if not rows:
        return "No transaction data available."

    n = len(rows)
    amounts = [r.total_amount for r in rows]
    total_revenue = sum(amounts)
    avg_transaction = total_revenue / n

    by_category = {}
    cat_counts = {}
    for r in rows:
        cat = r.product_category
        by_category[cat] = by_category.get(cat, 0) + r.total_amount
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    by_payment = {}
    for r in rows:
        pm = r.payment_method
        by_payment[pm] = by_payment.get(pm, 0) + r.total_amount

    unique_customers = len(set(r.customer_id for r in rows))
    unique_products = len(set(r.product_id for r in rows))

    lines = [
        f"Business Metrics — {n} transactions",
        f"═══════════════════════════════════════",
        f"",
        f"[Calculation Breakdown]",
        f"",
        f"Total Revenue = sum(TotalAmount for all {n} rows)",
        f"  = {_fmt(total_revenue)}",
        f"",
        f"Avg Transaction Value = Total Revenue / Transaction Count",
        f"  = {_fmt(total_revenue)} / {n}",
        f"  = {_fmt(avg_transaction)}",
        f"",
        f"Unique Customers = count(distinct CustomerID) = {unique_customers}",
        f"Unique Products = count(distinct ProductID) = {unique_products}",
        f"",
        f"Revenue by Category:",
        f"  (each = sum of TotalAmount WHERE ProductCategory = X)",
    ]
    for cat, rev in sorted(by_category.items(), key=lambda x: -x[1]):
        cnt = cat_counts[cat]
        lines.append(f"  • {cat}: {_fmt(rev)}  ({cnt} transactions, avg {_fmt(rev/cnt)})")

    lines.append(f"\nRevenue by Payment Method:")
    for pm, rev in sorted(by_payment.items(), key=lambda x: -x[1]):
        lines.append(f"  • {pm}: {_fmt(rev)}")

    return "\n".join(lines)


def compare_customers(id1: str, id2: str) -> str:
    """Compare two customers with calculation breakdowns."""
    def _stats(cid):
        rows = Transaction.query.filter_by(customer_id=cid).all()
        if not rows:
            return None, []
        return rows, rows

    rows1, _ = _stats(id1)
    rows2, _ = _stats(id2)

    if not rows1 and not rows2:
        return f"No transactions found for either customer {id1} or customer {id2}."
    if not rows1:
        return f"No transactions found for customer {id1}. Customer {id2} has data."
    if not rows2:
        return f"Customer {id1} has data. No transactions found for customer {id2}."

    def _breakdown(cid, rows):
        amounts = [r.total_amount for r in rows]
        n = len(rows)
        total = sum(amounts)
        avg = total / n
        categories = {}
        for r in rows:
            categories[r.product_category] = categories.get(r.product_category, 0) + r.total_amount
        payment_methods = {}
        for r in rows:
            payment_methods[r.payment_method] = payment_methods.get(r.payment_method, 0) + 1

        lines = [
            f"  Customer {cid}: {n} transaction(s)",
            f"  Total Spend = sum(TotalAmount)",
        ]
        if n <= 8:
            amt_str = " + ".join(f"${a:.2f}" for a in amounts)
            lines.append(f"    = {amt_str}")
        else:
            sample = amounts[:5]
            amt_str = " + ".join(f"${a:.2f}" for a in sample)
            lines.append(f"    = {amt_str} + ... ({n - 5} more)")
        lines.append(f"    = {_fmt(total)}")

        lines.append(f"  Avg per Transaction = {_fmt(total)} / {n} = {_fmt(avg)}")

        lines.append(f"  Categories:")
        for cat, val in sorted(categories.items()):
            lines.append(f"    • {cat}: {_fmt(val)}")

        lines.append(f"  Payment Methods:")
        for pm, cnt in sorted(payment_methods.items()):
            lines.append(f"    • {pm}: {cnt}x")

        return "\n".join(lines)

    lines = [
        f"Comparison: Customer {id1} vs Customer {id2}",
        f"═══════════════════════════════════════",
        f"",
        f"[Calculation Breakdown]",
        f"",
        _breakdown(id1, rows1),
        f"",
        _breakdown(id2, rows2),
    ]

    return "\n".join(lines)


def compare_products(id1: str, id2: str) -> str:
    """Compare two products with calculation breakdowns."""
    def _load(pid):
        rows = Transaction.query.filter_by(product_id=pid).all()
        return rows if rows else None

    rows1 = _load(id1)
    rows2 = _load(id2)

    if not rows1 and not rows2:
        return f"No transactions found for either product {id1} or product {id2}."
    if not rows1:
        return f"No transactions found for product {id1}. Product {id2} has data."
    if not rows2:
        return f"Product {id1} has data. No transactions found for product {id2}."

    def _breakdown(pid, rows):
        n = len(rows)
        quantities = [r.quantity for r in rows]
        amounts = [r.total_amount for r in rows]
        prices = [r.price for r in rows]
        discounts = [r.discount_applied for r in rows]

        total_qty = sum(quantities)
        total_rev = sum(amounts)
        sum_prices = sum(prices)
        avg_price = sum_prices / n
        sum_disc = sum(discounts)
        avg_disc = sum_disc / n
        store_count = len(set(r.store_location for r in rows))

        lines = [
            f"  Product {pid}: {n} transactions",
            f"  Total Qty = sum(Quantity) = {total_qty}",
            f"  Total Revenue = sum(TotalAmount) = {_fmt(total_rev)}",
            f"  Avg Price = sum(Price) / count = {_fmt(sum_prices)} / {n} = {_fmt(avg_price)}",
            f"  Avg Discount = sum(Discount) / count = {sum_disc:.2f} / {n} = {avg_disc:.1f}%",
            f"  Store Locations = count(distinct StoreLocation) = {store_count}",
        ]
        return "\n".join(lines)

    lines = [
        f"Comparison: Product {id1} vs Product {id2}",
        f"═══════════════════════════════════════",
        f"",
        f"[Calculation Breakdown]",
        f"",
        _breakdown(id1, rows1),
        f"",
        _breakdown(id2, rows2),
    ]

    return "\n".join(lines)
