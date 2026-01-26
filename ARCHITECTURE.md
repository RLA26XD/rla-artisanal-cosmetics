# RLA Artisanal Cosmetics - Technical Architecture

## System Overview

This document provides a detailed technical overview of the RLA Artisanal Cosmetics E-Commerce platform architecture.

---

## Architecture Pattern

**Model-View-Template (MVT)** with Blueprint-based modular routing

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                        │
│  (HTML + Tailwind CSS + Vanilla JavaScript)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓ HTTP Requests
┌─────────────────────────────────────────────────────────┐
│                   Flask Application                      │
│                      (app.py)                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Main BP    │  │ Products BP   │  │ Loyalty BP   │ │
│  │ (Homepage)   │  │ (Catalog)     │  │ (Rewards)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │        Dash Analytics Dashboard                    │ │
│  │        (Integrated at /admin/analytics)            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────┐
│                SQLite Database                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Products │  │Telemetry │  │  Users   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                    ┌──────────────┐                     │
│                    │LoyaltyAccounts│                     │
│                    └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Application Core (`app.py`)

**Responsibilities:**
- Flask app initialization using factory pattern
- Database initialization with SQLAlchemy
- Blueprint registration for modular routing
- Dash integration for analytics dashboard
- Error handler registration (404, 500)
- Session management

**Key Functions:**
```python
create_app(config_name)  # Factory pattern for app creation
register_blueprints(app)  # Modular route organization
init_dash(app)            # Dash analytics integration
```

---

### 2. Configuration (`config.py`)

**Purpose:** Centralized configuration management with environment-specific settings

**Classes:**
- `Config` - Base configuration
- `DevelopmentConfig` - Debug mode, local SQLite
- `ProductionConfig` - Production settings
- `TestingConfig` - Testing with in-memory DB

**Key Settings:**
```python
SQLALCHEMY_DATABASE_URI  # Database connection
INDIAN_STATES            # Geo-tracking list
REWARD_TIERS             # Loyalty tier thresholds
POINTS_PER_RUPEE         # Loyalty earning rate
```

---

### 3. Database Models

#### Product Model (`models/product.py`)
**Schema:**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    label VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,
    price_inr FLOAT,
    rating FLOAT,
    ingredients TEXT,
    description TEXT,
    image_url VARCHAR(500),
    stock_quantity INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Methods:**
- `get_all_brands()` - Retrieve unique brands
- `get_all_categories()` - Retrieve unique categories
- `filter_products()` - Advanced filtering with multiple criteria
- `to_dict()` - JSON serialization

#### Telemetry Model (`models/telemetry.py`)
**Purpose:** Track user behavior and analytics events

**Event Types:**
- `cart_addition` - Product added to cart
- `cart_abandonment` - User left without purchasing
- `category_click` - Category navigation
- `product_view` - Product detail page view
- `search` - Search query executed
- `page_view` - General page view

**Schema:**
```sql
CREATE TABLE telemetry (
    id INTEGER PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    product_id INTEGER,
    geo_state VARCHAR(50),
    geo_city VARCHAR(100),
    session_id VARCHAR(100),
    user_id INTEGER,
    event_data TEXT,
    category VARCHAR(100),
    search_term VARCHAR(200),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_agent VARCHAR(500),
    device_type VARCHAR(50),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**Analytics Methods:**
- `log_event()` - Create telemetry event
- `get_cart_abandonment_rate()` - Calculate abandonment percentage
- `get_top_states()` - Geographic analysis

#### User & Loyalty Models (`models/user.py`)

**User Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(15),
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    pincode VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);
```

**LoyaltyAccount Schema:**
```sql
CREATE TABLE loyalty_accounts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    points_balance INTEGER DEFAULT 0,
    lifetime_points INTEGER DEFAULT 0,
    tier VARCHAR(20) DEFAULT 'bronze',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Loyalty Logic:**
- Bronze: 0-999 points
- Silver: 1,000-4,999 points
- Gold: 5,000-9,999 points
- Platinum: 10,000+ points

---

### 4. Route Blueprints

#### Main Routes (`routes/main.py`)
```python
GET  /              # Landing page
GET  /about         # About page
GET  /contact       # Contact form
```

#### Products Routes (`routes/products.py`)
```python
GET  /products                    # Product listing with filters
GET  /products/<id>               # Product detail
GET  /products/search             # Search results
POST /products/api/add-to-cart    # Cart addition (telemetry)
POST /products/api/cart-abandonment  # Abandonment logging
```

**Filter Parameters:**
- `brand` - Filter by brand name
- `category` - Filter by category
- `min_price` - Minimum price (INR)
- `max_price` - Maximum price (INR)
- `min_rating` - Minimum rating threshold
- `page` - Pagination page number

#### Loyalty Routes (`routes/loyalty.py`)
```python
GET  /loyalty/rewards           # Rewards dashboard
POST /loyalty/api/add-points    # Add points (admin)
POST /loyalty/api/redeem-points # Redeem points
```

---

### 5. Analytics Dashboard (Dash Integration)

**URL:** `/admin/analytics`

**Architecture:**
```python
dash_app = dash.Dash(
    server=app,                          # Flask app
    url_base_pathname='/admin/analytics/',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
```

**Components:**
1. **KPI Cards:**
   - Cart Abandonment Rate (%)
   - Total Events (24h)
   - Total Active Products

2. **Visualizations:**
   - Events by Type (Bar Chart)
   - Geographic Distribution (Pie Chart)
   - Category Performance (Dual-axis Bar + Line)

3. **Real-time Updates:**
   - Auto-refresh interval: 30 seconds
   - Uses Dash callbacks with `dcc.Interval`

**Data Flow:**
```
Telemetry DB → SQLAlchemy Query → Pandas DataFrame → Plotly Chart → Dash Layout
```

---

### 6. Frontend Architecture

#### Technology Stack:
- **HTML5** with Jinja2 templating
- **Tailwind CSS 3.x** via CDN
- **Vanilla JavaScript** (no frameworks)
- **Google Fonts:** Playfair Display + Inter

#### Base Template (`templates/base.html`)
**Features:**
- Responsive navigation bar with mobile menu
- Search bar toggle
- Footer with newsletter signup
- Flash message support
- Custom CSS for luxury aesthetic

**CSS Classes:**
```css
.luxury-heading      # Playfair Display serif headers
.btn-primary         # Emerald gradient button
.btn-accent          # Saffron gradient button
.product-card        # Hover-animated product card
.nav-link            # Navigation link with underline effect
```

#### Page Templates:
1. `index.html` - Hero section + featured products
2. `products/index.html` - Filterable product grid
3. `products/detail.html` - Full product information
4. `loyalty/rewards.html` - Tier progress + redemption

---

### 7. Data Ingestion Pipeline

**Script:** `ingest_data.py`

**Workflow:**
```
Kaggle CSV → Pandas DataFrame → Data Cleaning → SQLAlchemy Models → SQLite DB
```

**Features:**
- Flexible column mapping (handles variations)
- Price conversion (USD → INR)
- Batch insertion (100 rows at a time)
- Error handling and skipping invalid rows
- Sample data generator for testing

**Usage:**
```bash
# From CSV
python ingest_data.py --csv data/cosmetics.csv --exchange-rate 83

# Sample data
python ingest_data.py --sample
```

---

## Design Patterns Used

### 1. Factory Pattern
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    # Configuration and initialization
    return app
```

### 2. Blueprint Pattern (Modular Routes)
```python
main_bp = Blueprint('main', __name__)
products_bp = Blueprint('products', __name__, url_prefix='/products')
loyalty_bp = Blueprint('loyalty', __name__, url_prefix='/loyalty')
```

### 3. Repository Pattern (in Models)
```python
@staticmethod
def filter_products(brand=None, category=None, ...):
    # Encapsulates complex queries
```

### 4. Decorator Pattern
```python
@login_required  # For future authentication
def protected_route():
    pass
```

---

## Security Considerations

### Current Implementation:
1. **Password Hashing:** Werkzeug's `generate_password_hash()`
2. **Session Management:** Flask's secure session cookies
3. **CSRF Protection:** Flask-WTF (to be implemented)
4. **SQL Injection Prevention:** SQLAlchemy ORM parameterized queries

### Production Recommendations:
1. Enable HTTPS/TLS
2. Implement proper user authentication
3. Add rate limiting for APIs
4. Use environment variables for secrets
5. Implement CSRF tokens on forms
6. Add input validation and sanitization

---

## Performance Optimization

### Database:
- **Indexes:** Brand, category, rating columns indexed
- **Pagination:** Limits query results to 12 per page
- **Lazy Loading:** Relationships loaded on-demand

### Frontend:
- **CDN:** Tailwind CSS loaded from CDN
- **Minimal JS:** No heavy frameworks
- **Image Optimization:** Lazy loading (to be implemented)

### Caching (Future):
- Flask-Caching for product queries
- Redis for session storage
- CDN for static assets

---

## Scalability Path

### Phase 1 (Current):
- SQLite database
- Single Flask process
- Static files served by Flask

### Phase 2 (Medium Scale):
- PostgreSQL database
- Gunicorn with multiple workers
- Nginx reverse proxy
- Static files on CDN

### Phase 3 (Large Scale):
- Database replication (read replicas)
- Load balancer (multiple app servers)
- Redis for caching and sessions
- Celery for async tasks (email, reports)
- Elasticsearch for product search

---

## Testing Strategy

### Unit Tests (Recommended):
```python
# Test product filtering
def test_filter_products_by_brand():
    products = Product.filter_products(brand='Himalaya')
    assert all(p.brand == 'Himalaya' for p in products)
```

### Integration Tests:
```python
# Test full request cycle
def test_product_detail_page(client):
    response = client.get('/products/1')
    assert response.status_code == 200
```

### Load Testing:
- Apache JMeter for load simulation
- Target: 100 concurrent users

---

## Monitoring & Logging

### Telemetry System:
- Tracks all user interactions
- Geographic distribution analysis
- Cart abandonment metrics

### Future Additions:
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Log aggregation (ELK stack)

---

## Deployment Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Configure production database (PostgreSQL)
- [ ] Set strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Configure logging to file
- [ ] Set up monitoring alerts
- [ ] Test error pages (404, 500)
- [ ] Optimize static assets

---

## Future Enhancements

1. **Authentication System:**
   - User registration/login
   - OAuth (Google, Facebook)
   - Email verification

2. **Shopping Cart:**
   - Persistent cart storage
   - Checkout process
   - Payment gateway integration

3. **Admin Panel:**
   - Product CRUD operations
   - User management
   - Order tracking

4. **Advanced Features:**
   - Product recommendations (ML)
   - Email marketing integration
   - Reviews and ratings system
   - Inventory management

---

## Contributing

When adding new features:
1. Create a new blueprint for major features
2. Add database models in `models/`
3. Write templates following the luxury design
4. Update this architecture document
5. Add telemetry logging for user actions

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Maintained By:** Development Team
