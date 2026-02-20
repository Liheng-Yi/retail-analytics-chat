from flask import Blueprint, jsonify
from app.models import Transaction

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/customers/<customer_id>")
def get_customer(customer_id):
    """Get all transactions for a specific customer."""
    rows = (
        Transaction.query
        .filter_by(customer_id=customer_id)
        .order_by(Transaction.transaction_date.desc())
        .limit(50)
        .all()
    )

    if not rows:
        return jsonify({"error": f"No transactions found for customer {customer_id}"}), 404

    total_spend = sum(r.total_amount for r in rows)

    return jsonify({
        "customer_id": customer_id,
        "transaction_count": len(rows),
        "total_spend": round(total_spend, 2),
        "transactions": [r.to_dict() for r in rows],
    })
