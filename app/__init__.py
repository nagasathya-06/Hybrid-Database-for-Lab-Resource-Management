# app/__init__.py
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register route blueprints
    from app.routes.equipment   import equipment_bp
    from app.routes.bookings    import bookings_bp
    from app.routes.maintenance import maintenance_bp

    app.register_blueprint(equipment_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(maintenance_bp)

    return app