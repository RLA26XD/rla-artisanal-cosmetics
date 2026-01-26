#!/bin/bash

# RLA Artisanal Cosmetics - Setup and Run Script

echo "🌟 RLA Artisanal Cosmetics E-Commerce Platform"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
if [ ! -f ".dependencies_installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch .dependencies_installed
    echo "✓ Dependencies installed"
    echo ""
fi

# Check if database exists
if [ ! -f "instance/cosmetics.db" ]; then
    echo "🗄️  Database not found. Creating with sample data..."
    python ingest_data.py --sample
    echo "✓ Database created with sample products"
    echo ""
else
    echo "✓ Database found"
    echo ""
fi

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
fi

echo "🚀 Starting Flask application..."
echo ""
echo "   Main Site: http://localhost:6969"
echo "   Analytics Dashboard: http://localhost:6969/admin/analytics"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Run the Flask app
python app.py
