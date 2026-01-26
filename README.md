# RLA Artisanal Cosmetics - E-Commerce Platform

A modern, full-stack e-commerce platform for Indian luxury cosmetics built with Flask, featuring analytics dashboard, loyalty rewards program, and telemetry tracking.

## 🎨 Design Philosophy

**Modern Indian Luxury** - A premium aesthetic combining:
- **Deep Emerald** (#022D1F) - Sophistication and trust
- **Saffron** (#F4C430) - Heritage and luxury
- **Clean White Space** - Minimalism and elegance

**Typography**:
- **Playfair Display** - Luxury headings with serif elegance
- **Inter** - Clean, modern body text

---

## 📁 Project Structure

```
rla-artisanal-cosmetics/
├── app.py                      # Main Flask application with Dash integration
├── config.py                   # Configuration settings
├── ingest_data.py             # CSV data ingestion script
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
│
├── models/                    # Database models
│   ├── __init__.py           # Database initialization
│   ├── product.py            # Product model
│   ├── telemetry.py          # Analytics/telemetry model
│   └── user.py               # User and loyalty models
│
├── routes/                    # Flask route blueprints
│   ├── __init__.py
│   ├── main.py               # Homepage routes
│   ├── products.py           # Product catalog routes
│   └── loyalty.py            # Rewards program routes
│
├── templates/                 # HTML templates (Jinja2)
│   ├── base.html             # Base template with navigation
│   ├── index.html            # Landing page
│   ├── about.html            # About page
│   ├── contact.html          # Contact page
│   ├── products/
│   │   ├── index.html        # Product listing with filters
│   │   └── detail.html       # Product detail page
│   ├── loyalty/
│   │   └── rewards.html      # Loyalty rewards page
│   └── errors/
│       ├── 404.html          # Not found error page
│       └── 500.html          # Server error page
│
├── static/                    # Static assets
│   ├── css/                  # Custom CSS files
│   ├── js/                   # JavaScript files
│   └── images/               # Image assets
│
├── data/                      # Data files
│   └── .gitkeep              # Place Kaggle CSV here
│
├── instance/                  # Instance folder (auto-created)
│   └── cosmetics.db          # SQLite database (auto-created)
│
└── utils/                     # Utility functions
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Kaggle E-commerce Cosmetics Dataset** (optional)

### Step 1: Set Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional)
```

### Step 3: Initialize Database

```bash
# Option A: Create with sample data
python ingest_data.py --sample

# Option B: Load from Kaggle CSV
# First, place your CSV in the data/ folder
python ingest_data.py --csv data/cosmetics.csv
```

### Step 4: Run the Application

```bash
# Start Flask development server
python app.py
```

The application will be available at:
- **Main Site**: http://localhost:6969
- **Analytics Dashboard**: http://localhost:6969/admin/analytics

---

## 📊 Features

### 1. Product Catalog Engine
- **Advanced Filtering**: Filter by brand, category, price range, and rating
- **Search Functionality**: Full-text search across products
- **Pagination**: Efficient product browsing
- **Product Details**: Complete product information with related items

### 2. Telemetry System
Tracks user behavior for analytics:
- `cart_addition` - Items added to cart
- `cart_abandonment` - Abandoned cart events
- `category_click` - Category navigation
- `product_view` - Product page views
- `search` - Search queries
- **Geo-location**: State and city tracking (Indian context)

### 3. Analytics Dashboard (Dash Integration)
Access at `/admin/analytics`:
- **Real-time KPIs**: Cart abandonment rate, total events, product count
- **Event Distribution**: Visualize user actions by type
- **Geographic Analysis**: Top states by activity
- **Category Performance**: Products and ratings by category
- **Auto-refresh**: Updates every 30 seconds

### 4. Loyalty Rewards Program
- **Tier System**: Bronze → Silver → Gold → Platinum
- **Points Earning**: 1 point per ₹1 spent
- **Progress Tracking**: Visual tier progression
- **Redemption Options**: Vouchers, free products, VIP experiences
- **Tier Benefits**: Escalating perks at each level

### 5. Modern UI/UX
- **Responsive Design**: Mobile-first with Tailwind CSS
- **Luxury Aesthetic**: Premium typography and color scheme
- **Smooth Animations**: Hover effects and transitions
- **Accessibility**: Semantic HTML and ARIA labels

---

## 🗄️ Database Models

### Product Model
```python
- id: Integer (Primary Key)
- brand: String (Brand name)
- label: String (Product name)
- category: String (Product category)
- price: Float (USD price)
- price_inr: Float (Indian Rupee price)
- rating: Float (Product rating)
- ingredients: Text (Ingredient list)
- description: Text (Product description)
- image_url: String (Product image)
- stock_quantity: Integer
- is_active: Boolean
```

### Telemetry Model
```python
- id: Integer (Primary Key)
- event_type: String (Event category)
- product_id: Integer (Foreign Key)
- geo_state: String (Indian state)
- geo_city: String (City name)
- session_id: String (Session identifier)
- user_id: Integer (User ID if logged in)
- timestamp: DateTime
- event_data: Text (JSON metadata)
```

### LoyaltyAccount Model
```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key to User)
- points_balance: Integer (Current points)
- lifetime_points: Integer (Total earned)
- tier: String (bronze/silver/gold/platinum)
```

---

## 🎯 Key Routes

### Public Routes
- `/` - Landing page with featured products
- `/products` - Product catalog with filters
- `/products/<id>` - Product detail page
- `/products/search` - Search results
- `/loyalty/rewards` - Loyalty rewards dashboard
- `/about` - About page
- `/contact` - Contact form

### API Endpoints
- `POST /products/api/add-to-cart` - Add item to cart (logs telemetry)
- `POST /products/api/cart-abandonment` - Log cart abandonment
- `POST /loyalty/api/add-points` - Add loyalty points
- `POST /loyalty/api/redeem-points` - Redeem points

### Admin Routes
- `/admin/analytics` - Dash analytics dashboard

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Indian States for geo-tracking
INDIAN_STATES = ['Maharashtra', 'Delhi', 'Karnataka', ...]

# Loyalty tiers and thresholds
REWARD_TIERS = {
    'bronze': 0,
    'silver': 1000,
    'gold': 5000,
    'platinum': 10000
}

# Points earning rate
POINTS_PER_RUPEE = 1
```

---

## 📦 Data Ingestion

### Using Kaggle Dataset

1. Download the E-commerce Cosmetics Dataset from Kaggle
2. Place CSV in `data/` folder
3. Run ingestion script:

```bash
python ingest_data.py --csv data/cosmetics.csv --exchange-rate 83
```

### Column Mapping

The script expects these columns (flexible):
- `Brand` or `brand`
- `Label`, `Name`, or `label`
- `Category` or `category`
- `Price` or `price`
- `Rating` or `rating`
- `Ingredients` (optional)
- `Description` (optional)
- `Image_URL` or `ImageURL` (optional)

---

## 🎨 Design Customization

### Color Scheme

Edit Tailwind config in `templates/base.html`:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                'emerald-deep': '#022D1F',  // Primary brand color
                'saffron': '#F4C430',        // Accent color
                'cream': '#FAF9F6',          // Background
            }
        }
    }
}
```

### Typography

Google Fonts are loaded in the `<head>`:
- Playfair Display: Luxury headings
- Inter: Body text

---

## 🔍 Analytics Dashboard Features

The integrated Dash dashboard provides:

1. **Cart Abandonment Rate**: Percentage of carts not converted to purchases
2. **Event Tracking**: Bar chart of user actions
3. **Geographic Distribution**: Pie chart of top 10 states
4. **Category Performance**: Dual-axis chart (product count + avg rating)
5. **Auto-refresh**: Real-time updates every 30 seconds

---

## 🛠️ Development Tips

### Running in Debug Mode

```bash
export FLASK_ENV=development
python app.py
```

### Database Reset

```bash
# Delete database
rm instance/cosmetics.db

# Reinitialize
python ingest_data.py --sample
```

### Adding New Models

1. Create model in `models/`
2. Import in `models/__init__.py`
3. Run `db.create_all()` in Flask shell

---

## 🚢 Production Deployment

### Environment Variables

Set these in production:

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://...  # Use PostgreSQL in production
```

### WSGI Server

Use Gunicorn for production:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Database Migration

For production, use PostgreSQL:

```python
# In config.py
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

---

## 📊 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.0 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **ORM** | SQLAlchemy 2.0 |
| **Analytics** | Dash 2.14 + Plotly 5.18 |
| **Frontend** | HTML5 + Tailwind CSS 3.x |
| **JavaScript** | Vanilla JS (minimal) |
| **Python** | 3.8+ |

---

## 🤝 Contributing

This is a learning/demonstration project. Feel free to:
- Fork and customize
- Add new features
- Improve the UI/UX
- Optimize database queries

---

## 📝 License

This project is open-source and available for educational purposes.

---

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Dash Plotly](https://dash.plotly.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 📧 Support

For questions or issues, refer to the documentation or Flask community resources.

---

**Built with ❤️ for showcasing modern Flask architecture and Indian luxury e-commerce**