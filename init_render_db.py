"""
Database initialization script for Render deployment
"""
import os
import sys
from pathlib import Path

# Add the project directory to the path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from models import db
from models.product import Product

def init_database():
    """Initialize database and import products"""
    print("🔧 Initializing database for Render...")
    
    # Create app with production config
    app = create_app('production')
    
    with app.app_context():
        # Ensure instance folder exists
        instance_path = Path(app.instance_path)
        instance_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Instance folder: {instance_path}")
        
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if products already exist
        product_count = Product.query.count()
        
        if product_count > 0:
            print(f"✓ Database already has {product_count:,} products")
            return
        
        # Import products from CSV
        csv_path = BASE_DIR / 'data' / 'cosmetics.csv'
        if not csv_path.exists():
            print(f"⚠️  CSV file not found at {csv_path}")
            print("   Skipping product import...")
            return
        
        print(f"📄 Found CSV file: {csv_path}")
        print("⏳ Importing products...")
        
        import pandas as pd
        
        # Read CSV with encoding handling
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            print("   ⚠️  UTF-8 decode failed, trying latin-1...")
            try:
                df = pd.read_csv(csv_path, encoding='latin-1')
            except Exception as e:
                print(f"   ❌ Failed to read CSV with latin-1: {e}")
                try:
                    df = pd.read_csv(csv_path, encoding='utf-8', errors='ignore')
                    print("   ✓ Read CSV with error handling (some characters may be skipped)")
                except Exception as e:
                    print(f"   ❌ Failed to read CSV: {e}")
                    return
        
        print(f"📊 CSV has {len(df):,} rows")
        
        # Import products in batches
        batch_size = 500
        imported = 0
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                try:
                    product = Product(
                        name=row.get('product_name', 'Unknown Product'),
                        brand=row.get('brand', 'Unknown'),
                        category=row.get('category', 'other').lower(),
                        subcategory=row.get('subcategory', ''),
                        price=float(row.get('price', 0)) if pd.notna(row.get('price')) else None,
                        rating=float(row.get('rating', 0)) if pd.notna(row.get('rating')) else None,
                        description=row.get('description', ''),
                        ingredients=row.get('ingredients', ''),
                        image_url=row.get('image_url', ''),
                        product_url=row.get('product_url', ''),
                        is_featured=bool(row.get('is_featured', False)),
                        stock_quantity=int(row.get('stock_quantity', 100)) if pd.notna(row.get('stock_quantity')) else 100
                    )
                    db.session.add(product)
                    imported += 1
                except Exception as e:
                    print(f"⚠️  Error importing row {imported + 1}: {str(e)}")
                    continue
            
            # Commit batch
            db.session.commit()
            print(f"   ✓ Imported {imported}/{len(df)} products...")
        
        print(f"✅ Successfully imported {imported:,} products")

if __name__ == '__main__':
    try:
        init_database()
        print("\n✅ Database initialization complete!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
