from flask import Blueprint, jsonify

products_bp = Blueprint("products", __name__)


@products_bp.route("/products/<product_id>")
def get_product(product_id):
    # TODO: implement data retrieval
    return jsonify({"message": f"Product {product_id} endpoint - not yet implemented"})
