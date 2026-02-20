"""OpenAI LLM service for retail analytics chat."""

import os
import json
import logging
from openai import OpenAI

from app.services.prompts import (
    SYSTEM_PROMPT,
    QUERY_CLASSIFICATION_PROMPT,
    RESPONSE_PROMPT,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


def get_openai_client():
    """Get configured OpenAI client."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)


def classify_query(question: str) -> dict:
    """
    Use GPT-4o-mini to classify user intent and extract entities.

    Returns:
        dict with keys: intent, customer_id, product_id, summary
    """
    client = get_openai_client()

    VALID_INTENTS = {"customer_query", "product_query", "business_metric", "comparison", "general"}

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intent classifier for a retail analytics system. "
                                   "Always respond with valid JSON only.",
                    },
                    {
                        "role": "user",
                        "content": QUERY_CLASSIFICATION_PROMPT.format(question=question),
                    },
                ],
                max_tokens=200,
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"Classification raw response: {content}")
            result = json.loads(content)

            # Normalize intent — if LLM returns something unexpected, map it
            intent = result.get("intent", "general").lower()
            if intent not in VALID_INTENTS:
                # Try to map common LLM-generated intents
                if "customer" in intent:
                    intent = "customer_query"
                elif "product" in intent:
                    intent = "product_query"
                elif any(w in intent for w in ("metric", "revenue", "business", "aggregate", "total")):
                    intent = "business_metric"
                else:
                    intent = "general"
            result["intent"] = intent

            # Normalize IDs to strings
            for key in ("customer_id", "customer_id_2", "product_id", "product_id_2"):
                if result.get(key) is not None:
                    result[key] = str(result[key])

            result.setdefault("summary", "")
            return result

        except Exception as e:
            logger.warning(f"classify_query attempt {attempt + 1} failed: {e}")

    # Fallback
    return {
        "intent": "general",
        "customer_id": None,
        "product_id": None,
        "summary": question,
    }


def generate_response(question: str, data: str) -> str:
    """
    Use GPT-4o-mini to generate a natural language response using retrieved data.

    Args:
        question: The user's original question
        data: Formatted string of data retrieved from the database

    Returns:
        Natural language response string
    """
    client = get_openai_client()

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": RESPONSE_PROMPT.format(
                            question=question, data=data
                        ),
                    },
                ],
                max_tokens=1000,
                temperature=0.5,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning(f"generate_response attempt {attempt + 1} failed: {e}")

    return "Sorry, I couldn't generate a response right now. Please try again."
