"""Chat endpoint — orchestrates LLM + data layer."""

import logging
from flask import Blueprint, jsonify, request

from app.services.llm_service import classify_query, generate_response
from app.services.data_service import (
    get_customer_transactions,
    get_product_info,
    get_business_metrics,
    compare_customers,
    compare_products,
)

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a question about retail data."})

    try:
        # Step 1: Classify intent and extract entities
        classification = classify_query(user_message)
        intent = classification.get("intent", "general")
        customer_id = classification.get("customer_id")
        customer_id_2 = classification.get("customer_id_2")
        product_id = classification.get("product_id")
        product_id_2 = classification.get("product_id_2")

        logger.info(f"Intent: {intent}, customer_id: {customer_id}, product_id: {product_id}")

        # Step 2: Retrieve data based on intent
        if intent == "comparison":
            if customer_id and customer_id_2:
                retrieved_data = compare_customers(customer_id, customer_id_2)
            elif product_id and product_id_2:
                retrieved_data = compare_products(product_id, product_id_2)
            else:
                retrieved_data = "Could not identify two entities to compare. Please specify two customer IDs or two product IDs."
        elif intent == "customer_query" and customer_id:
            retrieved_data = get_customer_transactions(customer_id)
        elif intent == "product_query" and product_id:
            retrieved_data = get_product_info(product_id)
        elif intent == "business_metric":
            retrieved_data = get_business_metrics()
        else:
            retrieved_data = "No specific data retrieval needed for this query."

        # Step 3: Generate natural language response
        response_text = generate_response(user_message, retrieved_data)

        return jsonify({"response": response_text})

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({
            "response": "Sorry, something went wrong processing your question. Please try again."
        }), 500
