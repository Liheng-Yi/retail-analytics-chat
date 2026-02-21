"""End-to-end tests for the /api/chat endpoint.

All LLM calls are mocked so no OpenAI API key is needed.
"""

import json
from unittest.mock import patch


# --------- helpers ---------

def _post_chat(client, message):
    return client.post(
        "/api/chat",
        data=json.dumps({"message": message}),
        content_type="application/json",
    )


def _mock_classify(intent, **extras):
    """Return a mock classification dict."""
    base = {
        "intent": intent,
        "customer_id": None,
        "customer_id_2": None,
        "product_id": None,
        "product_id_2": None,
        "summary": "test",
    }
    base.update(extras)
    return base


GENERATE_RESPONSE_PATH = "app.routes.chat.generate_response"
CLASSIFY_QUERY_PATH = "app.routes.chat.classify_query"


# --------- edge-case tests (no LLM mock needed) ---------

class TestEdgeCases:
    def test_empty_message(self, client):
        resp = _post_chat(client, "")
        data = resp.get_json()
        assert "Please enter a question" in data["response"]

    def test_message_too_long(self, client):
        resp = _post_chat(client, "x" * 501)
        data = resp.get_json()
        assert "500 characters" in data["response"]


# --------- customer query flow ---------

class TestCustomerQueryFlow:
    @patch(GENERATE_RESPONSE_PATH, return_value="Customer 109318 has 2 purchases.")
    @patch(CLASSIFY_QUERY_PATH, return_value=_mock_classify("customer_query", customer_id="109318"))
    def test_returns_source_data(self, mock_classify, mock_gen, client):
        resp = _post_chat(client, "What has customer 109318 purchased?")
        data = resp.get_json()

        assert resp.status_code == 200
        assert data["intent"] == "customer_query"
        assert "109318" in data["source_data"]
        assert data["response"] == "Customer 109318 has 2 purchases."

    @patch(GENERATE_RESPONSE_PATH, return_value="No data found for customer 000000.")
    @patch(CLASSIFY_QUERY_PATH, return_value=_mock_classify("customer_query", customer_id="000000"))
    def test_customer_not_found(self, mock_classify, mock_gen, client):
        resp = _post_chat(client, "Tell me about customer 000000")
        data = resp.get_json()
        assert "No transactions found" in data["source_data"]


# --------- product query flow ---------

class TestProductQueryFlow:
    @patch(GENERATE_RESPONSE_PATH, return_value="Product A info.")
    @patch(CLASSIFY_QUERY_PATH, return_value=_mock_classify("product_query", product_id="A"))
    def test_returns_charts(self, mock_classify, mock_gen, client):
        resp = _post_chat(client, "Tell me about product A")
        data = resp.get_json()

        assert resp.status_code == 200
        assert data["intent"] == "product_query"
        assert "chart_data" in data
        assert len(data["chart_data"]) == 2  # bar + pie

    @patch(GENERATE_RESPONSE_PATH, return_value="No data for product Z.")
    @patch(CLASSIFY_QUERY_PATH, return_value=_mock_classify("product_query", product_id="Z"))
    def test_product_not_found(self, mock_classify, mock_gen, client):
        resp = _post_chat(client, "Tell me about product Z")
        data = resp.get_json()
        assert "No transactions found" in data["source_data"]


# --------- business metric flow ---------

class TestBusinessMetricFlow:
    @patch(GENERATE_RESPONSE_PATH, return_value="Revenue breakdown here.")
    @patch(CLASSIFY_QUERY_PATH, return_value=_mock_classify("business_metric", metric_type="revenue"))
    def test_revenue_has_charts(self, mock_classify, mock_gen, client):
        resp = _post_chat(client, "What is the total revenue by category?")
        data = resp.get_json()

        assert resp.status_code == 200
        assert data["intent"] == "business_metric"
        assert "chart_data" in data
        assert len(data["chart_data"]) >= 1

    @patch(GENERATE_RESPONSE_PATH, return_value="There are 3 unique customers.")
    @patch(CLASSIFY_QUERY_PATH, return_value=_mock_classify("business_metric", metric_type="count"))
    def test_count_query_no_charts(self, mock_classify, mock_gen, client):
        resp = _post_chat(client, "How many unique customers are there?")
        data = resp.get_json()

        assert resp.status_code == 200
        assert data["intent"] == "business_metric"
        assert "chart_data" not in data


# --------- off-topic ---------

class TestOffTopic:
    @patch(CLASSIFY_QUERY_PATH, return_value=_mock_classify("off_topic"))
    def test_rejected(self, mock_classify, client):
        resp = _post_chat(client, "Tell me a joke")
        data = resp.get_json()
        assert data["intent"] == "off_topic"
        assert "retail analytics" in data["response"].lower()
