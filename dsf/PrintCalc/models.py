from app import db
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class AcademicYear(db.Model):
    """Model for academic years (e.g., أولى ابتدائي، ثانية ابتدائي)"""
    __tablename__ = 'academic_years'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationship with subjects
    subjects = relationship('Subject', backref='academic_year', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AcademicYear {self.name}>'

class Subject(db.Model):
    """Model for subjects within academic years (e.g., عربي، رياضيات، علوم)"""
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    year_id = Column(Integer, ForeignKey('academic_years.id'), nullable=False)
    
    # Relationship with books
    books = relationship('Book', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subject {self.name}>'

class Book(db.Model):
    """Model for books within subjects"""
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    page_count = Column(Integer, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    
    def __repr__(self):
        return f'<Book {self.name} ({self.page_count} pages)>'

class PrintingPrice(db.Model):
    """Model for printing prices and types"""
    __tablename__ = 'printing_prices'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "وش أسود", "وش وظهر أسود"
    price_per_unit = Column(Float, nullable=False)
    pages_per_unit = Column(Integer, nullable=False)  # How many pages per unit (2 for single-sided, 4 for double-sided)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f'<PrintingPrice {self.name}: {self.price_per_unit} per unit>'

class AddOn(db.Model):
    """Model for fixed add-ons like covers, binding, etc."""
    __tablename__ = 'addons'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f'<AddOn {self.name}: {self.price}>'

class Employee(db.Model):
    """Model for employees"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f'<Employee {self.username}>'

class Order(db.Model):
    """Model for customer orders"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String(100))
    customer_phone = Column(String(20))
    total_cost = Column(Float, nullable=False)
    status = Column(String(20), default='new')  # new, in_progress, completed
    printing_type_id = Column(Integer, ForeignKey('printing_prices.id'))
    selected_addons = Column(Text)  # JSON string of selected addons
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    
    # Relationships
    printing_type = relationship('PrintingPrice', backref='orders')
    employee = relationship('Employee', backref='orders')
    order_items = relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """Model for items in each order"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_cost = Column(Float, nullable=False)  # Cost per copy
    total_cost = Column(Float, nullable=False)  # Total cost for this item
    
    # Relationships
    book = relationship('Book', backref='order_items')
    
    def __repr__(self):
        return f'<OrderItem {self.book_id} x{self.quantity}>'
