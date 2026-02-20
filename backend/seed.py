"""Seed the PostgreSQL database from the CSV dataset."""

import csv
import os
import sys
from datetime import datetime

# Add parent dir to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Transaction

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "Retail_Transaction_Dataset.csv")
BATCH_SIZE = 5000


def seed():
    app = create_app()

    with app.app_context():
        # Check if already seeded
        count = Transaction.query.count()
        if count > 0:
            print(f"Database already has {count} rows. Skipping seed.")
            return

        print(f"Reading CSV from {CSV_PATH} ...")
        rows = []
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # Parse date — format is "M/D/YYYY H:MM"
                try:
                    tx_date = datetime.strptime(
                        row["TransactionDate"].strip(), "%m/%d/%Y %H:%M"
                    )
                except ValueError:
                    tx_date = datetime.strptime(
                        row["TransactionDate"].strip(), "%m/%d/%Y"
                    )

                t = Transaction(
                    customer_id=row["CustomerID"].strip(),
                    product_id=row["ProductID"].strip(),
                    quantity=int(row["Quantity"]),
                    price=float(row["Price"]),
                    transaction_date=tx_date,
                    payment_method=row["PaymentMethod"].strip(),
                    store_location=row["StoreLocation"].strip(),
                    product_category=row["ProductCategory"].strip(),
                    discount_applied=float(row["DiscountApplied(%)"]),
                    total_amount=float(row["TotalAmount"]),
                )
                rows.append(t)

                if len(rows) >= BATCH_SIZE:
                    db.session.bulk_save_objects(rows)
                    db.session.commit()
                    print(f"  Inserted {i + 1} rows ...")
                    rows = []

        # Insert remaining
        if rows:
            db.session.bulk_save_objects(rows)
            db.session.commit()

        final_count = Transaction.query.count()
        print(f"Done! Seeded {final_count} transactions.")


if __name__ == "__main__":
    seed()
