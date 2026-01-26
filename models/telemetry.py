"""
Telemetry Model for tracking user interactions and analytics
"""
from models import db
from datetime import datetime, timezone


class Telemetry(db.Model):
    """
    Telemetry model for tracking user behavior and analytics.
    Logs events like cart additions, abandonments, and category clicks.
    """
    __tablename__ = 'telemetry'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Event Information
    event_type = db.Column(db.String(50), nullable=False, index=True)
    # Event types: 'cart_addition', 'cart_abandonment', 'category_click', 
    #              'product_view', 'purchase', 'wishlist_add', 'search'
    
    # Product Reference (optional - not all events relate to products)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    
    # Geographic Information (Indian context)
    geo_state = db.Column(db.String(50), nullable=True, index=True)
    geo_city = db.Column(db.String(100), nullable=True)
    
    # Session Information
    session_id = db.Column(db.String(100), nullable=True, index=True)
    user_id = db.Column(db.Integer, nullable=True)  # For logged-in users
    
    # Event Metadata
    event_data = db.Column(db.Text, nullable=True)  # JSON string for additional data
    category = db.Column(db.String(100), nullable=True)  # For category_click events
    search_term = db.Column(db.String(200), nullable=True)  # For search events
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Device & Browser Information
    user_agent = db.Column(db.String(500), nullable=True)
    device_type = db.Column(db.String(50), nullable=True)  # mobile, tablet, desktop
    
    def __repr__(self):
        return f'<Telemetry {self.event_type} - {self.timestamp}>'
    
    def to_dict(self):
        """Convert telemetry event to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'product_id': self.product_id,
            'geo_state': self.geo_state,
            'geo_city': self.geo_city,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'event_data': self.event_data,
            'category': self.category,
            'search_term': self.search_term,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'device_type': self.device_type
        }
    
    @staticmethod
    def log_event(event_type, product_id=None, geo_state=None, geo_city=None, 
                  session_id=None, user_id=None, event_data=None, category=None,
                  search_term=None, user_agent=None, device_type=None):
        """
        Create and save a telemetry event.
        
        Args:
            event_type: Type of event (cart_addition, cart_abandonment, etc.)
            product_id: Related product ID (optional)
            geo_state: Indian state
            geo_city: City name
            session_id: User session identifier
            user_id: Logged-in user ID (optional)
            event_data: Additional JSON data
            category: Product category for category_click events
            search_term: Search query for search events
            user_agent: Browser user agent string
            device_type: mobile, tablet, or desktop
            
        Returns:
            Created Telemetry object
        """
        telemetry = Telemetry(
            event_type=event_type,
            product_id=product_id,
            geo_state=geo_state,
            geo_city=geo_city,
            session_id=session_id,
            user_id=user_id,
            event_data=event_data,
            category=category,
            search_term=search_term,
            user_agent=user_agent,
            device_type=device_type
        )
        db.session.add(telemetry)
        db.session.commit()
        return telemetry
    
    @staticmethod
    def get_events_by_type(event_type, limit=100):
        """Get recent events of a specific type."""
        return Telemetry.query.filter_by(event_type=event_type)\
            .order_by(Telemetry.timestamp.desc())\
            .limit(limit).all()
    
    @staticmethod
    def get_cart_abandonment_rate(days=30):
        """Calculate cart abandonment rate for the last N days."""
        from datetime import timedelta
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        cart_additions = db.session.query(func.count(Telemetry.id))\
            .filter(Telemetry.event_type == 'cart_addition')\
            .filter(Telemetry.timestamp >= start_date)\
            .scalar()
        
        purchases = db.session.query(func.count(Telemetry.id))\
            .filter(Telemetry.event_type == 'purchase')\
            .filter(Telemetry.timestamp >= start_date)\
            .scalar()
        
        if cart_additions > 0:
            abandonment_rate = ((cart_additions - purchases) / cart_additions) * 100
            return round(abandonment_rate, 2)
        return 0.0
    
    @staticmethod
    def get_top_states(limit=10):
        """Get top states by activity."""
        from sqlalchemy import func
        
        return db.session.query(
            Telemetry.geo_state,
            func.count(Telemetry.id).label('event_count')
        ).filter(Telemetry.geo_state.isnot(None))\
         .group_by(Telemetry.geo_state)\
         .order_by(func.count(Telemetry.id).desc())\
         .limit(limit).all()
