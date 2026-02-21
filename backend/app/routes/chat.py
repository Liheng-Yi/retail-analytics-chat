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
from app.services.chart_service import (
    build_product_charts,
    build_business_charts,
    build_comparison_charts,
)
from app.models import Transaction

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a question about retail data."})

    MAX_MESSAGE_LENGTH = 500
    if len(user_message) > MAX_MESSAGE_LENGTH:
        return jsonify({"response": f"Please keep your question under {MAX_MESSAGE_LENGTH} characters."})

    try:
        # Step 1: Classify intent and extract entities
        classification = classify_query(user_message)
        intent = classification.get("intent", "general")
        customer_id = classification.get("customer_id")
        customer_id_2 = classification.get("customer_id_2")
        product_id = classification.get("product_id")
        product_id_2 = classification.get("product_id_2")

        # Normalize customer IDs to uppercase for case-insensitive matching
        if customer_id:
            customer_id = customer_id.upper()
        if customer_id_2:
            customer_id_2 = customer_id_2.upper()
        if product_id:
            product_id = product_id.upper()
        if product_id_2:
            product_id_2 = product_id_2.upper()

        logger.info(f"Intent: {intent}, customer_id: {customer_id}, product_id: {product_id}")

        # Handle off-topic questions
        if intent == "off_topic":
            return jsonify({
                "response": "I'm a retail analytics assistant — I can only help with questions about customers, products, and business metrics from the transaction dataset. Try asking something like *\"What has customer 109318 purchased?\"*",
                "intent": "off_topic",
            })

        # Step 2: Load rows ONCE, use for both text + charts
        chart_data = None

        if intent == "comparison":
            if customer_id and customer_id_2:
                r1 = Transaction.query.filter_by(customer_id=customer_id).all()
                r2 = Transaction.query.filter_by(customer_id=customer_id_2).all()
                retrieved_data = compare_customers(customer_id, customer_id_2, r1, r2)
                if r1 and r2:
                    chart_data = build_comparison_charts("customer", customer_id, customer_id_2, r1, r2)
            elif product_id and product_id_2:
                r1 = Transaction.query.filter_by(product_id=product_id).all()
                r2 = Transaction.query.filter_by(product_id=product_id_2).all()
                retrieved_data = compare_products(product_id, product_id_2, r1, r2)
                if r1 and r2:
                    chart_data = build_comparison_charts("product", product_id, product_id_2, r1, r2)
            else:
                retrieved_data = "Could not identify two entities to compare."
        elif intent == "customer_query" and customer_id:
            retrieved_data = get_customer_transactions(customer_id)
        elif intent == "product_query" and product_id:
            rows = Transaction.query.filter_by(product_id=product_id).all()
            retrieved_data = get_product_info(product_id, rows)
            chart_data = build_product_charts(product_id, rows)
        elif intent == "business_metric":
            rows = Transaction.query.all()
            retrieved_data = get_business_metrics(rows)
            metric_type = classification.get("metric_type", "revenue")
            if metric_type == "revenue":
                chart_data = build_business_charts(rows)
        else:
            retrieved_data = "No specific data retrieval needed for this query."

        # Step 3: Generate natural language response
        response_text = generate_response(user_message, retrieved_data)

        result = {
            "response": response_text,
            "source_data": retrieved_data,
            "intent": intent,
        }
        if chart_data:
            result["chart_data"] = chart_data

        return jsonify(result)

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({
            "response": "Sorry, something went wrong processing your question. Please try again."
        }), 500
