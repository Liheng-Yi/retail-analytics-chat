from flask import Blueprint, jsonify
from sqlalchemy import func
from app.extensions import db
from app.models import Transaction

products_bp = Blueprint("products", __name__)


@products_bp.route("/products/<product_id>")
def get_product(product_id):
    """Get aggregated stats for a specific product ID."""
    rows = Transaction.query.filter_by(product_id=product_id).all()

    if not rows:
        return jsonify({"error": f"No transactions found for product {product_id}"}), 404

    total_qty = sum(r.quantity for r in rows)
    total_revenue = sum(r.total_amount for r in rows)
    avg_price = sum(r.price for r in rows) / len(rows)
    avg_discount = sum(r.discount_applied for r in rows) / len(rows)
    stores = sorted(set(r.store_location for r in rows))
    categories = sorted(set(r.product_category for r in rows))

    payment_methods = {}
    for r in rows:
        payment_methods[r.payment_method] = payment_methods.get(r.payment_method, 0) + 1

    return jsonify({
        "product_id": product_id,
        "transaction_count": len(rows),
        "categories": categories,
        "total_quantity_sold": total_qty,
        "total_revenue": round(total_revenue, 2),
        "average_price": round(avg_price, 2),
        "average_discount_pct": round(avg_discount, 2),
        "payment_methods": payment_methods,
        "store_count": len(stores),
        "sample_stores": stores[:20],
    })
