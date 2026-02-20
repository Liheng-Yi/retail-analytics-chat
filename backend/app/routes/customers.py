from flask import Blueprint, jsonify

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/customers/<customer_id>")
def get_customer(customer_id):
    # TODO: implement data retrieval
    return jsonify({"message": f"Customer {customer_id} endpoint - not yet implemented"})
