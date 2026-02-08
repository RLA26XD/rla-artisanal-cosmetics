"""
Configuration settings for the RLA Artisanal Cosmetics E-Commerce Platform
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Settings
    db_url = os.environ.get('DATABASE_URL')
    
    # Handle different database URL formats
    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Use /tmp for Railway (writable), instance for local
        db_dir = '/tmp' if os.environ.get('RAILWAY_ENVIRONMENT') else os.path.join(basedir, 'instance')
        os.makedirs(db_dir, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(db_dir, 'cosmetics.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Application Settings
    APP_NAME = "RLA Artisanal Cosmetics"
    ITEMS_PER_PAGE = 12
    
    # Indian States for Geo-location tracking
    INDIAN_STATES = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
        'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
        'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
        'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
        'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
        'Delhi', 'Puducherry', 'Jammu and Kashmir', 'Ladakh'
    ]
    
    # Loyalty Program Settings
    POINTS_PER_RUPEE = 1  # 1 point per rupee spent
    REWARD_TIERS = {
        'bronze': 0,
        'silver': 1000,
        'gold': 5000,
        'platinum': 10000
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
