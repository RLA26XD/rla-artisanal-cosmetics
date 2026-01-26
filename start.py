#!/usr/bin/env python3
"""
Universal startup script for RLA Artisanal Cosmetics
Handles database initialization and starts the appropriate server
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development').lower()
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', '6969'))
BASE_DIR = Path(__file__).parent
INSTANCE_DIR = BASE_DIR / 'instance'


def load_csv_data(app):
    """Load data from CSV file if available"""
    from app import db
    from models.product import Product
    
    data_dir = BASE_DIR / 'data'
    csv_files = list(data_dir.glob('*.csv')) if data_dir.exists() else []
    
    if not csv_files:
        print("   ℹ️  No CSV files found in data/ folder")
        return False
    
    csv_file = csv_files[0]
    print(f"   📄 Found CSV file: {csv_file.name}")
    print("   ⏳ Importing CSV data...")
    
    try:
        import pandas as pd
        
        # Read CSV with multiple encoding attempts
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_file, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print(f"   ⚠️  Could not read CSV file")
            return False
        
        print(f"   📊 CSV has {len(df)} rows")
        print(f"   📋 Columns: {', '.join(df.columns.tolist()[:5])}...")
        
        # Import products within app context
        with app.app_context():
            imported = 0
            skipped = 0
            
            for idx, row in df.iterrows():
                try:
                    # Map columns to Product model
                    # CSV columns: product_name, brand, category, subcategory, price, rating, ingredients
                    
                    # Get required fields
                    product_name = row.get('product_name') or row.get('Label') or row.get('Name')
                    brand = row.get('brand') or row.get('Brand')
                    
                    # Skip if missing required fields
                    if pd.isna(product_name) or pd.isna(brand) or not product_name or not brand:
                        skipped += 1
                        continue
                    
                    # Get category (use main category, not subcategory)
                    category = row.get('category') or row.get('subcategory') or row.get('Category') or 'Cosmetics'
                    
                    # Get price and convert to float
                    price_str = str(row.get('price', '0'))
                    # Remove currency symbols and commas
                    price_str = price_str.replace('$', '').replace('₹', '').replace(',', '').strip()
                    try:
                        price = float(price_str) if price_str and price_str != 'nan' else 0.0
                    except:
                        price = 0.0
                    
                    # Get rating
                    rating_val = row.get('rating')
                    try:
                        rating = float(rating_val) if pd.notna(rating_val) and rating_val != '' else None
                    except:
                        rating = None
                    
                    # Get optional fields
                    ingredients = str(row.get('ingredients', '')) if pd.notna(row.get('ingredients')) else None
                    form = str(row.get('form', '')) if pd.notna(row.get('form')) else None
                    color = str(row.get('color', '')) if pd.notna(row.get('color')) else None
                    
                    # Build description from available fields
                    desc_parts = []
                    if form:
                        desc_parts.append(f"Form: {form}")
                    if color:
                        desc_parts.append(f"Color: {color}")
                    description = '. '.join(desc_parts) if desc_parts else None
                    
                    # Create product
                    product = Product(
                        brand=str(brand)[:100],  # Limit to 100 chars
                        label=str(product_name)[:200],
                        category=str(category)[:100],
                        price=price,
                        price_inr=price * 83,  # USD to INR conversion
                        rating=rating,
                        ingredients=ingredients,
                        description=description,
                        image_url=None,
                        stock_quantity=100,
                        is_active=True
                    )
                    
                    db.session.add(product)
                    imported += 1
                    
                    # Commit in batches
                    if imported % 100 == 0:
                        db.session.commit()
                        print(f"   ⏳ Processed {imported} products...")
                        
                except Exception as e:
                    skipped += 1
                    if skipped < 5:  # Show first few errors
                        print(f"   ⚠️  Row {idx}: {e}")
                    continue
            
            # Final commit
            db.session.commit()
            print(f"   ✓ Imported {imported} products from CSV")
            if skipped > 0:
                print(f"   ⚠️  Skipped {skipped} rows (missing data)")
            return imported > 0
            
    except Exception as e:
        print(f"   ❌ CSV import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def init_database():
    """Initialize database folder and tables"""
    print("📦 Initializing database...")
    
    # Create instance directory FIRST (before importing app)
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ensure directory is writable
    test_file = INSTANCE_DIR / '.test'
    try:
        test_file.write_text('test')
        test_file.unlink()
    except Exception as e:
        print(f"   ❌ Instance folder not writable: {e}")
        sys.exit(1)
    
    print(f"   ✓ Instance folder: {INSTANCE_DIR}")
    
    # NOW import app (after folder is ready)
    from app import app, db
    from models.product import Product
    from models.telemetry import Telemetry  
    from models.user import User, LoyaltyAccount
    
    # Verify database URI
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    print(f"   ✓ Database URI: {db_uri}")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Count existing data
        product_count = db.session.query(Product).count()
        user_count = db.session.query(User).count()
        
        if product_count == 0:
            # Try to load CSV data
            csv_loaded = load_csv_data(app)
            
            if csv_loaded:
                # Recount after CSV import
                product_count = db.session.query(Product).count()
                print(f"   ✓ Database ready: {product_count} products loaded from CSV")
            else:
                print(f"   ✓ Database ready (empty - add CSV file to data/ folder)")
        else:
            print(f"   ✓ Database ready: {product_count} products, {user_count} users")
    
    return app


def start_development(app):
    """Start Flask development server"""
    print(f"\n{'='*60}")
    print("  🔧 DEVELOPMENT MODE")
    print(f"{'='*60}")
    print(f"  Server: Flask (debug mode, auto-reload)")
    print(f"  URL: http://{HOST}:{PORT}")
    print(f"  Debugger PIN: Will be shown below")
    print(f"{'='*60}\n")
    
    app.run(debug=True, host=HOST, port=PORT, use_reloader=True)


def start_production(app):
    """Start Gunicorn production server"""
    print(f"\n{'='*60}")
    print("  🚀 PRODUCTION MODE")
    print(f"{'='*60}")
    print(f"  Server: Gunicorn (multi-worker)")
    print(f"  URL: http://{HOST}:{PORT}")
    print(f"{'='*60}\n")
    
    import subprocess
    result = subprocess.run([
        'gunicorn',
        '-c', str(BASE_DIR / 'gunicorn_config.py'),
        'app:app'
    ])
    sys.exit(result.returncode)


def main():
    """Main entry point"""
    print(f"\n{'='*60}")
    print("  RLA Artisanal Cosmetics E-Commerce Platform")
    print(f"{'='*60}\n")
    
    try:
        # Initialize database first
        app = init_database()
        
        # Start appropriate server
        if FLASK_ENV == 'production':
            start_production(app)
        else:
            start_development(app)
            
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
