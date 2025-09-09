import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - use PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create all tables
    db.create_all()
    
    # Initialize default settings if they don't exist
    from models import PrintingPrice, AddOn, Employee
    from werkzeug.security import generate_password_hash
    
    # Create default printing prices if they don't exist
    if not PrintingPrice.query.first():
        default_prices = [
            PrintingPrice(name="وش أسود", price_per_unit=0.5, pages_per_unit=2),
            PrintingPrice(name="وش وظهر أسود", price_per_unit=0.8, pages_per_unit=4)
        ]
        for price in default_prices:
            db.session.add(price)
    
    # Create default add-ons if they don't exist
    if not AddOn.query.first():
        default_addons = [
            AddOn(name="غلاف", price=7.0, is_active=True),
            AddOn(name="تجليد", price=5.0, is_active=True)
        ]
        for addon in default_addons:
            db.session.add(addon)
    
    # Create default admin employee if no employees exist
    if not Employee.query.first():
        admin_employee = Employee(
            username="admin",
            password=generate_password_hash("admin123"),
            full_name="مدير النظام",
            phone="01000000000",
            is_active=True
        )
        db.session.add(admin_employee)
    
    db.session.commit()

# Import routes after app initialization
import routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
