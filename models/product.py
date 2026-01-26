"""
Product Model for E-Commerce Cosmetics Database
"""
from models import db
from datetime import datetime, timezone


class Product(db.Model):
    """
    Product model representing cosmetic items in the database.
    Based on Kaggle E-commerce Cosmetics Dataset schema.
    """
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False, index=True)
    label = db.Column(db.String(200), nullable=False)  # Product name
    category = db.Column(db.String(100), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    price_inr = db.Column(db.Float, nullable=True)  # Price in Indian Rupees
    rating = db.Column(db.Float, nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    stock_quantity = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    telemetry_events = db.relationship('Telemetry', backref='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.brand} - {self.label}>'
    
    def to_dict(self):
        """Convert product to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'brand': self.brand,
            'label': self.label,
            'category': self.category,
            'price': self.price,
            'price_inr': self.price_inr,
            'rating': self.rating,
            'ingredients': self.ingredients,
            'description': self.description,
            'image_url': self.image_url,
            'stock_quantity': self.stock_quantity,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_all_brands():
        """Get list of all unique brands."""
        return db.session.query(Product.brand).distinct().order_by(Product.brand).all()
    
    @staticmethod
    def get_all_categories():
        """Get list of all unique categories."""
        return db.session.query(Product.category).distinct().order_by(Product.category).all()
    
    @staticmethod
    def filter_products(brand=None, category=None, min_price=None, max_price=None, min_rating=None):
        """
        Filter products based on various criteria.
        
        Args:
            brand: Filter by brand name
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rating: Minimum rating filter
            
        Returns:
            Query object with filtered products
        """
        query = Product.query.filter_by(is_active=True)
        
        if brand:
            query = query.filter(Product.brand == brand)
        if category:
            query = query.filter(Product.category == category)
        if min_price:
            query = query.filter(Product.price_inr >= min_price)
        if max_price:
            query = query.filter(Product.price_inr <= max_price)
        if min_rating:
            query = query.filter(Product.rating >= min_rating)
            
        return query
