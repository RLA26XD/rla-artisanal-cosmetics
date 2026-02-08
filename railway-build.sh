#!/usr/bin/env bash
# Railway build script

echo "🚂 Railway Build Starting..."

# Install dependencies
pip install -r requirements.txt

# Initialize database
echo "📦 Initializing database..."
python init_db.py || echo "⚠️  Database initialization skipped (may already exist)"

echo "✅ Railway Build Complete!"
