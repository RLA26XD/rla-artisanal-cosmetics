#!/usr/bin/env python
"""
Quick setup script for RLA Artisanal Cosmetics
Creates database and initializes with sample data
"""

import os
import sys

# Ensure we're in the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🌟 RLA Artisanal Cosmetics - Quick Setup")
print("=" * 50)
print()

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Error: Python 3.8 or higher is required")
    print(f"   Current version: {sys.version}")
    sys.exit(1)

print("✓ Python version OK")
print()

# Create instance directory
os.makedirs('instance', exist_ok=True)
print("✓ Instance directory created")

# Check if database exists
db_exists = os.path.exists('instance/cosmetics.db')

if db_exists:
    response = input("Database already exists. Recreate? (y/N): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        sys.exit(0)
    os.remove('instance/cosmetics.db')
    print("✓ Old database removed")

# Initialize database
print()
print("Creating database with sample data...")
print("-" * 50)

from app import app, db
from models.product import Product
from models.telemetry import Telemetry
from models.user import User, LoyaltyAccount

with app.app_context():
    # Create tables
    db.create_all()
    print("✓ Database tables created")
    
    # Create sample products
    sample_products = [
        {
            'brand': 'Himalaya',
            'label': 'Nourishing Face Cream',
            'category': 'Skincare',
            'price': 12.99,
            'price_inr': 1078.17,
            'rating': 4.5,
            'description': 'Natural face cream enriched with herbal extracts for deeply nourished and radiant skin.',
            'stock_quantity': 50
        },
        {
            'brand': 'Lakme',
            'label': 'Absolute Matte Lipstick',
            'category': 'Face Makeup',
            'price': 8.99,
            'price_inr': 746.17,
            'rating': 4.3,
            'description': 'Long-lasting matte lipstick in vibrant colors for all-day wear.',
            'stock_quantity': 75
        },
        {
            'brand': 'Forest Essentials',
            'label': 'Luxury Face Serum with Saffron',
            'category': 'Skincare',
            'price': 45.00,
            'price_inr': 3735.00,
            'rating': 4.8,
            'description': 'Premium face serum with natural oils, saffron, and botanical extracts for age-defying radiance.',
            'stock_quantity': 30
        },
        {
            'brand': 'MyGlamm',
            'label': 'HD Makeup Foundation',
            'category': 'Face Makeup',
            'price': 15.99,
            'price_inr': 1327.17,
            'rating': 4.4,
            'description': 'High-definition foundation for flawless, natural-looking coverage.',
            'stock_quantity': 60
        },
        {
            'brand': 'Kama Ayurveda',
            'label': 'Pure Rose Water Face Toner',
            'category': 'Skincare',
            'price': 18.50,
            'price_inr': 1535.50,
            'rating': 4.6,
            'description': 'Ayurvedic rose water toner for refreshed, balanced, and glowing skin.',
            'stock_quantity': 40
        },
        {
            'brand': 'Sugar Cosmetics',
            'label': 'Nothing Else Matter Longwear Lipstick',
            'category': 'Face Makeup',
            'price': 10.99,
            'price_inr': 911.17,
            'rating': 4.5,
            'description': 'Transfer-proof matte lipstick with intense color payoff.',
            'stock_quantity': 80
        },
        {
            'brand': 'Biotique',
            'label': 'Bio Morning Nectar Moisturizer',
            'category': 'Skincare',
            'price': 14.50,
            'price_inr': 1203.50,
            'rating': 4.2,
            'description': 'Lightweight moisturizer with honey and wheat germ for soft, supple skin.',
            'stock_quantity': 55
        },
        {
            'brand': 'Colorbar',
            'label': 'Perfect Match Compact Powder',
            'category': 'Face Makeup',
            'price': 12.50,
            'price_inr': 1037.50,
            'rating': 4.1,
            'description': 'Lightweight compact powder for a natural, shine-free finish.',
            'stock_quantity': 65
        }
    ]
    
    for product_data in sample_products:
        product = Product(**product_data)
        db.session.add(product)
    
    db.session.commit()
    print(f"✓ Created {len(sample_products)} sample products")
    
    # Create demo user with loyalty account
    demo_user = User(
        email='demo@rlacosmetics.com',
        first_name='Demo',
        last_name='User',
        city='Mumbai',
        state='Maharashtra'
    )
    demo_user.set_password('demo123')
    db.session.add(demo_user)
    db.session.commit()
    
    loyalty = LoyaltyAccount(
        user_id=demo_user.id,
        points_balance=2500,
        lifetime_points=2500
    )
    loyalty.update_tier()
    db.session.add(loyalty)
    db.session.commit()
    
    print("✓ Created demo user account")
    print("  Email: demo@rlacosmetics.com")
    print("  Password: demo123")

print()
print("=" * 50)
print("✅ Setup Complete!")
print()
print("To start the application:")
print("  1. Activate virtual environment: source venv/bin/activate")
print("  2. Run: python app.py")
print()
print("Or use the quick start script: ./run.sh")
print()
print("URLs:")
print("  Main Site: http://localhost:6969")
print("  Analytics: http://localhost:6969/admin/analytics")
print("=" * 50)
