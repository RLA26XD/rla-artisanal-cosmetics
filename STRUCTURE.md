# 📁 Complete Folder Structure

## Visual Project Organization

```
rla-artisanal-cosmetics/
│
├── 📄 app.py                          # Main Flask application entry point
├── 📄 config.py                       # Configuration settings (dev/prod)
├── 📄 ingest_data.py                 # CSV data loading script
├── 📄 setup.py                       # Quick setup automation script
├── 📄 run.sh                         # Bash script to run application
│
├── 📄 requirements.txt               # Python dependencies
├── 📄 .env.example                   # Environment variables template
├── 📄 .gitignore                     # Git ignore rules
│
├── 📄 README.md                      # Main documentation
├── 📄 ARCHITECTURE.md                # Technical architecture guide
├── 📄 QUICKSTART.md                  # 5-minute quick start guide
├── 📄 STRUCTURE.md                   # This file - folder structure
│
├── 📂 models/                        # Database Models (SQLAlchemy)
│   ├── 📄 __init__.py               # DB initialization
│   ├── 📄 product.py                # Product model
│   ├── 📄 telemetry.py              # Analytics/tracking model
│   └── 📄 user.py                   # User & loyalty models
│
├── 📂 routes/                        # Flask Blueprints (URL Routes)
│   ├── 📄 __init__.py               # Routes initialization
│   ├── 📄 main.py                   # Homepage & general pages
│   ├── 📄 products.py               # Product catalog routes
│   └── 📄 loyalty.py                # Rewards program routes
│
├── 📂 templates/                     # HTML Templates (Jinja2)
│   ├── 📄 base.html                 # Base template (nav, footer)
│   ├── 📄 index.html                # Landing page with hero
│   ├── 📄 about.html                # About page
│   ├── 📄 contact.html              # Contact form page
│   │
│   ├── 📂 products/                 # Product templates
│   │   ├── 📄 index.html            # Product listing with filters
│   │   ├── 📄 detail.html           # Product detail page
│   │   └── 📄 search.html           # Search results (optional)
│   │
│   ├── 📂 loyalty/                  # Loyalty program templates
│   │   └── 📄 rewards.html          # Rewards dashboard
│   │
│   └── 📂 errors/                   # Error page templates
│       ├── 📄 404.html              # Page not found
│       └── 📄 500.html              # Server error
│
├── 📂 static/                        # Static Assets
│   ├── 📂 css/                      # Custom stylesheets
│   │   └── (place custom CSS here)
│   │
│   ├── 📂 js/                       # JavaScript files
│   │   └── (place custom JS here)
│   │
│   └── 📂 images/                   # Image assets
│       └── (place images, logo here)
│
├── 📂 utils/                         # Utility Functions
│   ├── 📄 __init__.py
│   └── 📄 helpers.py                # Helper functions
│
├── 📂 data/                          # Data Files
│   └── 📄 .gitkeep                  # Place Kaggle CSV here
│
├── 📂 instance/                      # Instance Folder (auto-generated)
│   └── 📄 cosmetics.db              # SQLite database (auto-created)
│
└── 📂 venv/                          # Virtual Environment (auto-created)
    └── (Python packages installed here)
```

---

## File Descriptions

### Root Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| `app.py` | Main application, Flask setup, Dash integration | Adding new blueprints, middleware |
| `config.py` | Configuration (database, tiers, states) | Changing settings, tiers, rewards |
| `ingest_data.py` | Load CSV data into database | Modifying data import logic |
| `setup.py` | Automated setup script | Never (unless improving automation) |
| `run.sh` | Quick start bash script | Customizing startup process |
| `requirements.txt` | Python package dependencies | Adding new libraries |
| `.env.example` | Environment variables template | Adding new config variables |

---

### Documentation Files

| File | Content | Audience |
|------|---------|----------|
| `README.md` | Complete project documentation | All users |
| `ARCHITECTURE.md` | Technical architecture details | Developers |
| `QUICKSTART.md` | 5-minute getting started | New users |
| `STRUCTURE.md` | This file - folder organization | Contributors |

---

### Models Directory (`models/`)

**Purpose:** Database schema definitions using SQLAlchemy ORM

| File | Model Classes | Description |
|------|---------------|-------------|
| `__init__.py` | `db` object | SQLAlchemy database instance |
| `product.py` | `Product` | Cosmetic products catalog |
| `telemetry.py` | `Telemetry` | User behavior tracking |
| `user.py` | `User`, `LoyaltyAccount` | Users and rewards |

**Relationships:**
```
Product ←→ Telemetry (one-to-many)
User ←→ LoyaltyAccount (one-to-one)
```

---

### Routes Directory (`routes/`)

**Purpose:** URL routing logic organized by feature

| File | Blueprint | URL Prefix | Purpose |
|------|-----------|------------|---------|
| `main.py` | `main_bp` | `/` | Homepage, about, contact |
| `products.py` | `products_bp` | `/products` | Catalog, search, filters |
| `loyalty.py` | `loyalty_bp` | `/loyalty` | Rewards dashboard |

**Route Examples:**
```
/                              → main_bp.index()
/products                      → products_bp.index()
/products/<id>                 → products_bp.detail(id)
/products/api/add-to-cart      → products_bp.add_to_cart()
/loyalty/rewards               → loyalty_bp.rewards()
/admin/analytics               → Dash app (in app.py)
```

---

### Templates Directory (`templates/`)

**Purpose:** HTML templates with Jinja2 syntax

#### Base Template
- `base.html` - Master layout with navigation, footer, CSS/JS

#### Page Templates
```
index.html              → Landing page (hero + featured products)
about.html              → Brand story
contact.html            → Contact form

products/
  index.html            → Product grid with sidebar filters
  detail.html           → Single product page with related items

loyalty/
  rewards.html          → Points dashboard with tier progress

errors/
  404.html              → Page not found
  500.html              → Server error
```

**Template Inheritance:**
```
base.html
  ├── index.html
  ├── about.html
  ├── products/index.html
  ├── products/detail.html
  ├── loyalty/rewards.html
  └── errors/*.html
```

---

### Static Directory (`static/`)

**Purpose:** CSS, JavaScript, and images served directly

```
static/
├── css/
│   └── custom.css          (add your own styles)
│
├── js/
│   └── main.js             (add custom JavaScript)
│
└── images/
    ├── logo.png            (brand logo)
    ├── hero-bg.jpg         (hero background)
    └── product-*.jpg       (product images)
```

**Note:** Tailwind CSS is loaded from CDN in base.html

---

### Utils Directory (`utils/`)

**Purpose:** Helper functions and utilities

| File | Functions |
|------|-----------|
| `helpers.py` | Session management, currency formatting, device detection |

**Example Functions:**
```python
get_or_create_session_id()    # Session handling
format_currency(amount)         # ₹1,234.56
calculate_loyalty_points()      # Points calculation
detect_device_type()            # mobile/tablet/desktop
```

---

### Data Directory (`data/`)

**Purpose:** Store CSV files for import

```
data/
├── .gitkeep
└── cosmetics.csv           (place your Kaggle CSV here)
```

**Usage:**
```bash
python ingest_data.py --csv data/cosmetics.csv
```

---

### Instance Directory (`instance/`)

**Purpose:** Auto-generated folder for database

```
instance/
└── cosmetics.db            (SQLite database file)
```

**Note:** 
- Created automatically on first run
- Ignored by Git (.gitignore)
- Contains all data (products, users, telemetry)

---

### Virtual Environment (`venv/`)

**Purpose:** Isolated Python environment

```
venv/
├── bin/                    (Python executables)
├── lib/                    (Installed packages)
└── pyvenv.cfg              (Configuration)
```

**Note:** Ignored by Git, created with `python -m venv venv`

---

## File Counts

| Type | Count |
|------|-------|
| Python Files | 15 |
| HTML Templates | 11 |
| Documentation | 4 |
| Configuration | 3 |
| Scripts | 2 |

---

## Which Files to Edit?

### Common Customizations

| Want to... | Edit this file... |
|-----------|------------------|
| Change colors | `templates/base.html` (Tailwind config) |
| Add new product fields | `models/product.py` |
| Modify loyalty tiers | `config.py` (REWARD_TIERS) |
| Add new page | Create in `templates/`, add route in `routes/` |
| Change homepage content | `templates/index.html` |
| Add custom styles | `static/css/custom.css` (create it) |
| Modify navigation | `templates/base.html` |
| Add analytics event | `models/telemetry.py` |

### Advanced Customizations

| Want to... | Edit these files... |
|-----------|---------------------|
| Add payment gateway | Create `routes/checkout.py`, add templates |
| Implement authentication | `models/user.py`, add login routes |
| Add product reviews | Create `models/review.py`, update product detail |
| Email notifications | Create `utils/email.py`, update relevant routes |

---

## Import Paths Reference

```python
# Models
from models import db
from models.product import Product
from models.telemetry import Telemetry
from models.user import User, LoyaltyAccount

# Config
from config import Config

# Helpers
from utils.helpers import format_currency, calculate_loyalty_points

# Flask
from flask import render_template, request, jsonify, session
```

---

## Database Location

**Development:**
```
instance/cosmetics.db           (SQLite)
```

**Production (Recommended):**
```
PostgreSQL on separate server
URI: postgresql://user:pass@host:5432/dbname
```

---

## Logs and Cache

Currently not implemented. To add:

```
logs/
├── app.log                     (Application logs)
└── error.log                   (Error logs)

cache/
└── (cached query results)
```

---

## Best Practices

### ✅ Do:
- Keep models in `models/`
- Organize routes by feature (blueprints)
- Extend base template for consistency
- Use utility functions for common tasks
- Document new features

### ❌ Don't:
- Put business logic in templates
- Mix routes and models in one file
- Edit `venv/` or `instance/` directly
- Commit `.env` or database files
- Hardcode configuration values

---

## Quick Navigation

| I want to... | Go to... |
|-------------|---------|
| Understand architecture | `ARCHITECTURE.md` |
| Get started quickly | `QUICKSTART.md` |
| See full documentation | `README.md` |
| Find a specific file | This file (`STRUCTURE.md`) |
| Modify database schema | `models/` directory |
| Change page layouts | `templates/` directory |
| Add routes/APIs | `routes/` directory |

---

**Last Updated:** January 2026  
**Version:** 1.0
