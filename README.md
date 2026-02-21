# 📊 Retail Analytics Chat

An AI-powered retail analytics system that lets users query transaction data through a conversational chat interface. Built with **React**, **Flask**, **PostgreSQL**, and **OpenAI GPT-4o**.

## Local Setup & Run

```bash
# 1. Clone the repository
git clone https://github.com/Liheng-Yi/retail-analytics-chat.git
cd retail-analytics-chat

# 2. Add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > backend/.env

# 3. Start all services
docker compose up

# 4. Seed the database (first run only — run in a separate terminal)
docker compose exec backend python seed.py
```

Once running, open:
- **Chat UI:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:5000](http://localhost:5000)
- **pgAdmin (optional):** [http://localhost:5050](http://localhost:5050) — login: `admin@admin.com` / `admin`

**Query flow:**
1. User sends a natural language question via the chat UI
2. Backend sends the question to GPT-4o-mini for **intent classification** (customer, product, business metric, comparison, or off-topic)
3. Backend extracts entity IDs and queries PostgreSQL accordingly
4. Retrieved data is sent to GPT-4o to generate a **natural language response**
5. Response + optional charts are returned to the frontend

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | React 19, Vite, Recharts            |
| Backend   | Python, Flask, SQLAlchemy           |
| Database  | PostgreSQL 16                       |
| LLM       | OpenAI GPT-4o + GPT-4o-mini         |
| Infra     | Docker Compose                      |

## Prerequisites

- Docker Desktop
- OpenAI API key

## Dataset Setup

The project uses the [Kaggle Retail Transaction Dataset](https://www.kaggle.com/datasets/fahadrehman07/retail-transaction-dataset/data).

The CSV file is already included at `backend/data/Retail_Transaction_Dataset.csv`. If you need to re-download it, place it in `backend/data/`

## Environment Variables

Create a `backend/.env` file with your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-key-here
```

## Example Queries

### Customer Queries
- `What has customer 109318 purchased?`
- `How much has customer 993229 spent in total?`
- `Show me the purchase history for customer 109318`

### Product Queries
- `Which stores sell product B?`
- `Tell me about product D`

### Business Metrics
- `What is the total revenue by category?`
- `How many unique customers are there?`

### Comparison Queries (Bonus)
- `Compare product A vs product B`
- `Compare customer 109318 vs customer 993229`

### Edge Case Handling
- `Tell me a joke` → Politely rejected as off-topic
- Empty message → Prompted to enter a question
- Non-existent ID → Clear "no data found" message
- chat character limit

## Key Technical Decisions

- **Intent classification via LLM** — GPT-4o-mini classifies each query into one of: `customer_query`, `product_query`, `business_metric`, `comparison`, `off_topic`, or `general`. This avoids brittle regex-based routing.
- **Two-pass LLM approach** — First call uses GPT-4o-mini (fast/cheap) to classify intent and extract IDs; second call uses GPT-4o (higher quality) to generate the natural language response from retrieved data. This balances cost and quality.
- **PostgreSQL over SQLite** — Chosen for indexed queries on `customer_id` and `product_id` columns, better concurrency, and production readiness.
- **Structured chart data** — Backend returns chart-ready JSON; frontend renders it with Recharts. No image generation needed.
- **Edge case handling** — Off-topic detection, input length cap (500 chars), case-insensitive ID matching, and graceful error responses.
