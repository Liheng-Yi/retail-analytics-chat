from app.extensions import db


class Transaction(db.Model):
    """Retail transaction record from the Kaggle dataset."""
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.String(20), nullable=False, index=True)
    product_id = db.Column(db.String(20), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    store_location = db.Column(db.Text, nullable=False)
    product_category = db.Column(db.String(100), nullable=False)
    discount_applied = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
            "transaction_date": self.transaction_date.isoformat(),
            "payment_method": self.payment_method,
            "store_location": self.store_location,
            "product_category": self.product_category,
            "discount_applied": self.discount_applied,
            "total_amount": self.total_amount,
        }
