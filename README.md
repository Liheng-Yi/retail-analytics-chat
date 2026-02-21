# Retail Analytics Chat

An AI-powered retail analytics system that lets users query transaction data through a conversational chat interface. Built with **React**, **Flask**, **PostgreSQL**, and **OpenAI GPT-4o**.

## Prerequisites

- Docker Desktop
- OpenAI API key

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

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | React 19, Vite, Recharts            |
| Backend   | Python, Flask, SQLAlchemy           |
| Database  | PostgreSQL 16                       |
| LLM       | OpenAI GPT-4o + GPT-4o-mini         |
| Infra     | Docker Compose                      |


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
<img width="907" height="1197" alt="image" src="https://github.com/user-attachments/assets/7ff9b54a-b179-4159-90c4-17f7ca79cf5b" />

<img width="653" height="988" alt="image" src="https://github.com/user-attachments/assets/e85429b6-ba12-426b-a717-c6d0536d5930" />

