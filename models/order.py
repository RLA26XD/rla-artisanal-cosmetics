"""
Order model for tracking customer purchases.
"""
from datetime import datetime
from models import db

class Order(db.Model):
    """Model for customer orders."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)  # e.g., ORD-20260208-001
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Order details
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, shipped, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    
    # Shipping information
    shipping_name = db.Column(db.String(200), nullable=False)
    shipping_email = db.Column(db.String(200), nullable=False)
    shipping_phone = db.Column(db.String(20), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_postal_code = db.Column(db.String(20), nullable=False)
    shipping_country = db.Column(db.String(100), nullable=False, default='India')
    
    # Additional info
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    def get_status_badge_class(self):
        """Return Bootstrap badge class based on order status."""
        status_classes = {
            'pending': 'warning',
            'confirmed': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return status_classes.get(self.status, 'secondary')


class OrderItem(db.Model):
    """Model for individual items within an order."""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item details (snapshot at time of purchase)
    product_name = db.Column(db.String(500), nullable=False)
    product_brand = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Float, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('order_items', lazy=True))
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'
