"""Build structured chart data for frontend visualizations.

All functions accept pre-loaded rows to avoid duplicate DB queries.
"""


def build_product_charts(product_id, rows):
    """Return chart data for a product query from pre-loaded rows."""
    if not rows:
        return None

    cat_rev = {}
    pm_counts = {}
    for r in rows:
        cat_rev[r.product_category] = cat_rev.get(r.product_category, 0) + r.total_amount
        pm_counts[r.payment_method] = pm_counts.get(r.payment_method, 0) + 1

    return [
        {
            "type": "bar",
            "title": f"Product {product_id} — Revenue by Category",
            "data": [{"name": k, "value": round(v, 2)} for k, v in sorted(cat_rev.items())],
            "dataKey": "value",
            "color": "#6c63ff",
        },
        {
            "type": "pie",
            "title": f"Product {product_id} — Payment Methods",
            "data": [{"name": k, "value": v} for k, v in sorted(pm_counts.items())],
        },
    ]


def build_business_charts(rows):
    """Return chart data for business metrics from pre-loaded rows."""
    if not rows:
        return None

    cat_rev = {}
    pm_rev = {}
    for r in rows:
        cat_rev[r.product_category] = cat_rev.get(r.product_category, 0) + r.total_amount
        pm_rev[r.payment_method] = pm_rev.get(r.payment_method, 0) + r.total_amount

    return [
        {
            "type": "bar",
            "title": "Revenue by Category",
            "data": [{"name": k, "value": round(v, 2)} for k, v in sorted(cat_rev.items(), key=lambda x: -x[1])],
            "dataKey": "value",
            "color": "#6c63ff",
        },
        {
            "type": "pie",
            "title": "Revenue by Payment Method",
            "data": [{"name": k, "value": round(v, 2)} for k, v in sorted(pm_rev.items())],
        },
    ]


def build_comparison_charts(kind, id1, id2, rows1, rows2):
    """Return chart data for comparison queries."""
    if kind == "customer":
        return _customer_comparison_charts(id1, id2, rows1, rows2)
    return _product_comparison_charts(id1, id2, rows1, rows2)


def _customer_comparison_charts(id1, id2, rows1, rows2):
    cats1, cats2 = {}, {}
    for r in rows1:
        cats1[r.product_category] = cats1.get(r.product_category, 0) + r.total_amount
    for r in rows2:
        cats2[r.product_category] = cats2.get(r.product_category, 0) + r.total_amount
    all_cats = sorted(set(list(cats1) + list(cats2)))

    return [
        {
            "type": "grouped_bar",
            "title": f"Spending by Category — Customer {id1} vs {id2}",
            "data": [
                {"name": cat, f"Customer {id1}": round(cats1.get(cat, 0), 2), f"Customer {id2}": round(cats2.get(cat, 0), 2)}
                for cat in all_cats
            ],
            "keys": [f"Customer {id1}", f"Customer {id2}"],
            "colors": ["#6c63ff", "#a78bfa"],
        },
    ]


def _product_comparison_charts(id1, id2, rows1, rows2):
    def _s(rows):
        n = len(rows)
        return {
            "transactions": n,
            "qty": sum(r.quantity for r in rows),
            "revenue": round(sum(r.total_amount for r in rows), 2),
            "avg_price": round(sum(r.price for r in rows) / n, 2),
        }

    s1, s2 = _s(rows1), _s(rows2)

    return [
        {
            "type": "grouped_bar",
            "title": f"Product {id1} vs {id2} — Revenue & Avg Price",
            "data": [
                {"name": "Total Revenue", f"Product {id1}": s1["revenue"], f"Product {id2}": s2["revenue"]},
            ],
            "keys": [f"Product {id1}", f"Product {id2}"],
            "colors": ["#6c63ff", "#a78bfa"],
        },
        {
            "type": "grouped_bar",
            "title": f"Product {id1} vs {id2} — Volume",
            "data": [
                {"name": "Transactions", f"Product {id1}": s1["transactions"], f"Product {id2}": s2["transactions"]},
                {"name": "Qty Sold", f"Product {id1}": s1["qty"], f"Product {id2}": s2["qty"]},
            ],
            "keys": [f"Product {id1}", f"Product {id2}"],
            "colors": ["#6c63ff", "#a78bfa"],
        },
    ]
