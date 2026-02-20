from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.customers import customers_bp
    from app.routes.products import products_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(customers_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")

    # Create tables
    with app.app_context():
        from app.models import Transaction  # noqa: F401
        db.create_all()

    return app
