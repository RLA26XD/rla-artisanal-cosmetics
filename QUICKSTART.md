# Quick Start Guide - RLA Artisanal Cosmetics

Get up and running in **5 minutes**! 🚀

---

## Prerequisites

✅ **Python 3.8 or higher**  
✅ **pip** (Python package manager)  
✅ **Terminal/Command Line** access

---

## Method 1: Automated Setup (Recommended)

### Step 1: Run Setup Script

```bash
python setup.py
```

This will:
- ✓ Check Python version
- ✓ Create database with sample products
- ✓ Set up demo user account
- ✓ Display access URLs

### Step 2: Activate Virtual Environment

```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Start the Application

```bash
python app.py
```

**Or use the quick start script:**

```bash
chmod +x run.sh
./run.sh
```

---

## Method 2: Manual Setup

### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Create Environment File

```bash
cp .env.example .env
```

### Step 4: Initialize Database

**Option A - Sample Data:**
```bash
python ingest_data.py --sample
```

**Option B - From Kaggle CSV:**
```bash
# Place CSV in data/ folder
python ingest_data.py --csv data/cosmetics.csv
```

### Step 5: Run Application

```bash
python app.py
```

---

## Access Your Application

Once running, open your browser:

### 🏠 Main Website
**URL:** http://localhost:6969

**Features:**
- Browse product catalog
- Search and filter products
- View product details
- Check loyalty rewards

### 📊 Analytics Dashboard
**URL:** http://localhost:6969/admin/analytics

**Features:**
- Real-time KPIs
- Cart abandonment metrics
- Geographic distribution
- Category performance

---

## Default Credentials

**Demo User Account:**
- **Email:** demo@rlacosmetics.com
- **Password:** demo123
- **Loyalty Points:** 2,500 (Silver tier)

---

## Testing the Application

### 1. Browse Products
1. Go to http://localhost:6969
2. Click "Explore Collection"
3. Use filters: Brand, Category, Price, Rating
4. Click any product for details

### 2. View Rewards
1. Click "Rewards" in navigation
2. See tier progress and points balance
3. View redemption options

### 3. Check Analytics
1. Navigate to http://localhost:6969/admin/analytics
2. Watch real-time dashboard
3. Auto-refreshes every 30 seconds

---

## Common Commands

### Start Application
```bash
python app.py
```

### Reset Database
```bash
rm instance/cosmetics.db
python ingest_data.py --sample
```

### Run in Debug Mode
```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python app.py
```

### Install New Package
```bash
pip install package-name
pip freeze > requirements.txt
```

---

## Project Structure Reference

```
rla-artisanal-cosmetics/
├── app.py              ← Main application
├── config.py           ← Configuration
├── ingest_data.py      ← Data loading
├── requirements.txt    ← Dependencies
│
├── models/             ← Database models
│   ├── product.py
│   ├── telemetry.py
│   └── user.py
│
├── routes/             ← URL routes
│   ├── main.py
│   ├── products.py
│   └── loyalty.py
│
├── templates/          ← HTML files
│   ├── base.html
│   ├── index.html
│   └── products/
│
└── static/             ← CSS, JS, Images
    ├── css/
    ├── js/
    └── images/
```

---

## Customization Quick Tips

### Change Colors

Edit `templates/base.html`:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                'emerald-deep': '#022D1F',  // Your color here
                'saffron': '#F4C430',        // Your color here
            }
        }
    }
}
```

### Add Products

Edit `ingest_data.py` or use Python shell:

```python
from app import app, db
from models.product import Product

with app.app_context():
    product = Product(
        brand='Your Brand',
        label='Product Name',
        category='Skincare',
        price_inr=1500,
        rating=4.5
    )
    db.session.add(product)
    db.session.commit()
```

### Modify Loyalty Tiers

Edit `config.py`:

```python
REWARD_TIERS = {
    'bronze': 0,
    'silver': 1000,
    'gold': 5000,
    'platinum': 10000
}
```

---

## Troubleshooting

### Issue: "Port 5000 already in use"

**Solution:**
```bash
# Change port in app.py (last line)
app.run(debug=True, port=6969)
```

### Issue: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Database locked"

**Solution:**
```bash
rm instance/cosmetics.db
python ingest_data.py --sample
```

### Issue: "Templates not found"

**Solution:**
Ensure you're running from project root directory:
```bash
cd /path/to/rla-artisanal-cosmetics
python app.py
```

---

## Next Steps

1. ✅ **Explore the Code**
   - Check `models/` for database structure
   - Review `routes/` for API endpoints
   - Examine `templates/` for UI

2. ✅ **Add Your Data**
   - Download Kaggle cosmetics dataset
   - Run: `python ingest_data.py --csv data/your-file.csv`

3. ✅ **Customize Design**
   - Modify colors in `base.html`
   - Update content in templates
   - Add your logo to `static/images/`

4. ✅ **Add Features**
   - Implement shopping cart
   - Add user authentication
   - Create admin panel

---

## Resources

- **Documentation:** See `README.md` for full details
- **Architecture:** See `ARCHITECTURE.md` for technical details
- **Flask Docs:** https://flask.palletsprojects.com/
- **Tailwind CSS:** https://tailwindcss.com/docs

---

## Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review error messages in terminal
3. Verify Python version: `python --version`
4. Ensure all dependencies installed: `pip list`

---

## Development Tips

### Live Reload
Flask auto-reloads on code changes when `debug=True`

### Database Changes
After modifying models, recreate database:
```bash
rm instance/cosmetics.db
python setup.py
```

### Add Custom CSS
Create `static/css/custom.css` and link in `base.html`

### Add JavaScript
Create `static/js/main.js` and link in `base.html`

---

**Happy Coding! 🎨✨**

---

**Version:** 1.0  
**Last Updated:** January 2026
