from flask import Blueprint, jsonify, request

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    # TODO: implement LLM integration and query routing
    return jsonify({
        "response": f"Echo: {user_message} (LLM not yet connected)"
    })
