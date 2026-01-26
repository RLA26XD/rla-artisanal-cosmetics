"""
Data Ingestion Script
Loads Kaggle E-commerce Cosmetics Dataset CSV into SQLite database
"""
import pandas as pd
import os
import sys
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models.product import Product


def clean_price(price_str):
    """
    Clean price string and convert to float.
    Handles various formats like '$25.99', '₹1,250', etc.
    """
    if pd.isna(price_str):
        return None
    
    # Remove currency symbols and commas
    price_str = str(price_str).replace('$', '').replace('₹', '').replace(',', '').strip()
    
    try:
        return float(price_str)
    except ValueError:
        return None


def convert_to_inr(price_usd, exchange_rate=83.0):
    """
    Convert USD price to INR.
    Default exchange rate: 1 USD = 83 INR (approximate)
    """
    if price_usd is None:
        return None
    return round(price_usd * exchange_rate, 2)


def ingest_csv(csv_path, exchange_rate=83.0):
    """
    Ingest CSV data into the database.
    
    Args:
        csv_path: Path to the Kaggle CSV file
        exchange_rate: USD to INR conversion rate
    
    Returns:
        Number of products imported
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return 0
    
    print(f"Reading CSV from {csv_path}...")
    # Try different encodings to handle various CSV formats
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"Successfully read CSV with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        print("Error: Could not read CSV with any supported encoding")
        return 0
    
    print(f"Found {len(df)} rows in CSV")
    print(f"Columns: {df.columns.tolist()}")
    
    # Map CSV columns to Product model fields
    # Adjust these column names based on your actual Kaggle dataset
    column_mapping = {
        'Brand': 'brand',
        'Label': 'label',
        'Name': 'label',  # Alternative column name
        'Category': 'category',
        'Price': 'price',
        'Rating': 'rating',
        'Ingredients': 'ingredients',
        'Description': 'description',
        'Image_URL': 'image_url',
        'ImageURL': 'image_url',  # Alternative column name
    }
    
    imported_count = 0
    skipped_count = 0
    
    with app.app_context():
        # Clear existing products (optional - comment out to append)
        # Product.query.delete()
        # db.session.commit()
        # print("Cleared existing products")
        
        for idx, row in df.iterrows():
            try:
                # Extract data with flexible column mapping
                brand = None
                label = None
                category = None
                price = None
                rating = None
                
                # Try to find brand
                if 'Brand' in df.columns:
                    brand = row['Brand']
                elif 'brand' in df.columns:
                    brand = row['brand']
                
                # Try to find label/name
                if 'Label' in df.columns:
                    label = row['Label']
                elif 'Name' in df.columns:
                    label = row['Name']
                elif 'label' in df.columns:
                    label = row['label']
                
                # Try to find category
                if 'Category' in df.columns:
                    category = row['Category']
                elif 'category' in df.columns:
                    category = row['category']
                
                # Try to find price
                if 'Price' in df.columns:
                    price = clean_price(row['Price'])
                elif 'price' in df.columns:
                    price = clean_price(row['price'])
                
                # Try to find rating
                if 'Rating' in df.columns:
                    rating = row['Rating'] if pd.notna(row['Rating']) else None
                elif 'rating' in df.columns:
                    rating = row['rating'] if pd.notna(row['rating']) else None
                
                # Skip if essential fields are missing
                if not brand or not label:
                    skipped_count += 1
                    continue
                
                # Get optional fields
                ingredients = row.get('Ingredients', None) if 'Ingredients' in df.columns else None
                description = row.get('Description', None) if 'Description' in df.columns else None
                image_url = row.get('Image_URL', row.get('ImageURL', None))
                
                # Convert price to INR
                price_inr = convert_to_inr(price, exchange_rate) if price else None
                
                # Create product
                product = Product(
                    brand=str(brand),
                    label=str(label),
                    category=str(category) if category else 'Uncategorized',
                    price=price if price else 0.0,
                    price_inr=price_inr if price_inr else 0.0,
                    rating=float(rating) if rating and pd.notna(rating) else None,
                    ingredients=str(ingredients) if ingredients and pd.notna(ingredients) else None,
                    description=str(description) if description and pd.notna(description) else None,
                    image_url=str(image_url) if image_url and pd.notna(image_url) else None,
                    stock_quantity=100,
                    is_active=True
                )
                
                db.session.add(product)
                imported_count += 1
                
                # Commit in batches of 100
                if imported_count % 100 == 0:
                    db.session.commit()
                    print(f"Imported {imported_count} products...")
                
            except Exception as e:
                print(f"Error importing row {idx}: {e}")
                skipped_count += 1
                continue
        
        # Final commit
        db.session.commit()
        print(f"\nImport complete!")
        print(f"Successfully imported: {imported_count} products")
        print(f"Skipped: {skipped_count} rows")
    
    return imported_count


def create_sample_data():
    """
    Create sample data if no CSV is available.
    Useful for testing the application structure.
    """
    sample_products = [
        {
            'brand': 'Himalaya',
            'label': 'Nourishing Face Cream',
            'category': 'Skincare',
            'price': 12.99,
            'price_inr': 1078.17,
            'rating': 4.5,
            'description': 'Natural face cream with herbal extracts for nourished skin.',
            'stock_quantity': 50
        },
        {
            'brand': 'Lakme',
            'label': 'Absolute Matte Lipstick',
            'category': 'Face Makeup',
            'price': 8.99,
            'price_inr': 746.17,
            'rating': 4.3,
            'description': 'Long-lasting matte lipstick in vibrant colors.',
            'stock_quantity': 75
        },
        {
            'brand': 'Forest Essentials',
            'label': 'Luxury Face Serum',
            'category': 'Skincare',
            'price': 45.00,
            'price_inr': 3735.00,
            'rating': 4.8,
            'description': 'Premium face serum with natural oils and botanical extracts.',
            'stock_quantity': 30
        },
        {
            'brand': 'MyGlamm',
            'label': 'HD Makeup Foundation',
            'category': 'Face Makeup',
            'price': 15.99,
            'price_inr': 1327.17,
            'rating': 4.4,
            'description': 'High-definition foundation for flawless coverage.',
            'stock_quantity': 60
        },
        {
            'brand': 'Kama Ayurveda',
            'label': 'Rose Face Toner',
            'category': 'Skincare',
            'price': 18.50,
            'price_inr': 1535.50,
            'rating': 4.6,
            'description': 'Ayurvedic rose water toner for refreshed skin.',
            'stock_quantity': 40
        }
    ]
    
    with app.app_context():
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"Created {len(sample_products)} sample products")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest cosmetics data into database')
    parser.add_argument('--csv', type=str, help='Path to CSV file')
    parser.add_argument('--sample', action='store_true', help='Create sample data instead')
    parser.add_argument('--exchange-rate', type=float, default=83.0, 
                       help='USD to INR exchange rate (default: 83.0)')
    
    args = parser.parse_args()
    
    if args.sample:
        print("Creating sample data...")
        create_sample_data()
    elif args.csv:
        print(f"Ingesting data from {args.csv}...")
        ingest_csv(args.csv, args.exchange_rate)
    else:
        print("Please provide either --csv path or --sample flag")
        print("Example: python ingest_data.py --csv data/cosmetics.csv")
        print("Example: python ingest_data.py --sample")
