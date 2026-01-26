"""
User and Loyalty Program Models
"""
from models import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User model for customer accounts."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    
    # Address Information
    address_line1 = db.Column(db.String(200), nullable=True)
    address_line2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    loyalty_account = db.relationship('LoyaltyAccount', backref='user', uselist=False)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'phone': self.phone,
            'city': self.city,
            'state': self.state,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LoyaltyAccount(db.Model):
    """Loyalty rewards account for customers."""
    __tablename__ = 'loyalty_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Points and Tier
    points_balance = db.Column(db.Integer, default=0)
    lifetime_points = db.Column(db.Integer, default=0)
    tier = db.Column(db.String(20), default='bronze')  # bronze, silver, gold, platinum
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<LoyaltyAccount User:{self.user_id} Points:{self.points_balance}>'
    
    def add_points(self, points):
        """Add points to the account and update tier."""
        self.points_balance += points
        self.lifetime_points += points
        self.update_tier()
        db.session.commit()
    
    def redeem_points(self, points):
        """Redeem points (does not affect tier)."""
        if self.points_balance >= points:
            self.points_balance -= points
            db.session.commit()
            return True
        return False
    
    def update_tier(self):
        """Update loyalty tier based on lifetime points."""
        from config import Config
        
        if self.lifetime_points >= Config.REWARD_TIERS['platinum']:
            self.tier = 'platinum'
        elif self.lifetime_points >= Config.REWARD_TIERS['gold']:
            self.tier = 'gold'
        elif self.lifetime_points >= Config.REWARD_TIERS['silver']:
            self.tier = 'silver'
        else:
            self.tier = 'bronze'
    
    def get_next_tier_info(self):
        """Get information about the next tier."""
        from config import Config
        
        tiers = ['bronze', 'silver', 'gold', 'platinum']
        current_index = tiers.index(self.tier)
        
        if current_index < len(tiers) - 1:
            next_tier = tiers[current_index + 1]
            points_needed = Config.REWARD_TIERS[next_tier] - self.lifetime_points
            return {
                'next_tier': next_tier,
                'points_needed': points_needed,
                'progress_percentage': (self.lifetime_points / Config.REWARD_TIERS[next_tier]) * 100
            }
        return {
            'next_tier': None,
            'points_needed': 0,
            'progress_percentage': 100
        }
    
    def to_dict(self):
        """Convert loyalty account to dictionary."""
        next_tier_info = self.get_next_tier_info()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'points_balance': self.points_balance,
            'lifetime_points': self.lifetime_points,
            'tier': self.tier,
            'next_tier': next_tier_info['next_tier'],
            'points_to_next_tier': next_tier_info['points_needed'],
            'progress_percentage': next_tier_info['progress_percentage']
        }
