# 🌊 RLA Artisanal Cosmetics - Data Flow Diagrams

## Complete System Architecture Flow

---

## 1. Application Startup Flow

```
User runs: python app.py
        │
        ↓
┌───────────────────────────────────────────────────────┐
│ app.py: create_app(config_name='development')        │
│                                                       │
│  1. Load Configuration from config.py                │
│  2. Initialize SQLAlchemy database                   │
│  3. Create instance/ folder if missing               │
│  4. Create all database tables (db.create_all)       │
│  5. Register blueprints (main, products, loyalty)    │
│  6. Initialize Dash analytics dashboard              │
│  7. Register error handlers (404, 500)               │
│  8. Set up before_request handlers                   │
└────────────────────┬──────────────────────────────────┘
                     │
                     ↓
        Flask Dev Server Starts
                     │
                     ↓
        Listening on http://localhost:6969
```

---

## 2. Request-Response Flow

```
User visits: http://localhost:6969/products

        │ HTTP GET Request
        ↓
┌───────────────────────────────────┐
│   Flask Application (app.py)      │
└────────────┬──────────────────────┘
             │
             ↓ Route Matching
┌───────────────────────────────────┐
│  products_bp.index() in           │
│  routes/products.py               │
│                                   │
│  1. Parse query parameters        │
│     (brand, category, price, etc.)│
│                                   │
│  2. Build database query          │
└────────────┬──────────────────────┘
             │
             ↓ SQLAlchemy Query
┌───────────────────────────────────┐
│  Product.filter_products()        │
│  in models/product.py             │
│                                   │
│  SELECT * FROM products           │
│  WHERE category = 'Skincare'      │
│  AND price_inr >= 1000            │
│  ORDER BY rating DESC             │
│  LIMIT 12 OFFSET 0                │
└────────────┬──────────────────────┘
             │
             ↓ Query Results
┌───────────────────────────────────┐
│  Database (instance/cosmetics.db) │
│                                   │
│  Returns: List of Product objects │
└────────────┬──────────────────────┘
             │
             ↓ Render Template
┌───────────────────────────────────┐
│  templates/products/index.html    │
│                                   │
│  Jinja2 renders with:             │
│  - products list                  │
│  - brands for filter              │
│  - categories for filter          │
│  - pagination info                │
└────────────┬──────────────────────┘
             │
             ↓ HTML Response
        User's Browser
```

---

## 3. Telemetry Tracking Flow

```
User clicks "Add to Cart" button

        │ JavaScript fetch() API call
        ↓
POST /products/api/add-to-cart
        │
        ↓
┌───────────────────────────────────┐
│  products_bp.add_to_cart()        │
│  in routes/products.py            │
│                                   │
│  1. Parse JSON: {product_id: 5}   │
│  2. Validate product exists       │
│  3. Get session_id from session   │
│  4. Extract geo data (if provided)│
└────────────┬──────────────────────┘
             │
             ↓ Log Event
┌───────────────────────────────────┐
│  Telemetry.log_event()            │
│  in models/telemetry.py           │
│                                   │
│  INSERT INTO telemetry VALUES (   │
│    event_type='cart_addition',    │
│    product_id=5,                  │
│    session_id='abc-123',          │
│    geo_state='Maharashtra',       │
│    timestamp=now()                │
│  )                                │
└────────────┬──────────────────────┘
             │
             ↓ Commit to DB
┌───────────────────────────────────┐
│  Database (instance/cosmetics.db) │
│  ✅ Event logged successfully     │
└────────────┬──────────────────────┘
             │
             ↓ JSON Response
        {success: true, message: "Added to cart"}
        │
        ↓
    JavaScript updates UI
    (cart count, success message)
```

---

## 4. Analytics Dashboard Flow

```
User visits: http://localhost:6969/admin/analytics

        │ HTTP GET Request
        ↓
┌───────────────────────────────────┐
│  Dash App (initialized in app.py)│
│                                   │
│  URL: /admin/analytics/           │
│  Server: Flask app                │
└────────────┬──────────────────────┘
             │
             ↓ Render Layout
┌───────────────────────────────────┐
│  dash_app.layout                  │
│                                   │
│  Components:                      │
│  - KPI cards                      │
│  - Event chart (dcc.Graph)        │
│  - Geo chart (dcc.Graph)          │
│  - Category chart (dcc.Graph)     │
│  - Auto-refresh (dcc.Interval)    │
└────────────┬──────────────────────┘
             │
             ↓ Initial Data Load
┌───────────────────────────────────┐
│  Dash Callback Function           │
│  update_dashboard(n_intervals)    │
│                                   │
│  Every 30 seconds, execute:       │
└────────────┬──────────────────────┘
             │
             ↓ Query Database
┌───────────────────────────────────┐
│  Multiple SQLAlchemy Queries:     │
│                                   │
│  1. Cart abandonment rate         │
│     SELECT COUNT(*) cart_adds...  │
│     SELECT COUNT(*) purchases...  │
│                                   │
│  2. Events by type                │
│     SELECT event_type, COUNT(*)   │
│     GROUP BY event_type           │
│                                   │
│  3. Geographic distribution       │
│     SELECT geo_state, COUNT(*)    │
│     GROUP BY geo_state            │
│                                   │
│  4. Category performance          │
│     SELECT category, COUNT(*),    │
│            AVG(rating)            │
│     GROUP BY category             │
└────────────┬──────────────────────┘
             │
             ↓ Convert to DataFrames
┌───────────────────────────────────┐
│  Pandas DataFrames                │
│                                   │
│  events_df = pd.DataFrame(...)    │
│  geo_df = pd.DataFrame(...)       │
│  category_df = pd.DataFrame(...)  │
└────────────┬──────────────────────┘
             │
             ↓ Create Plotly Charts
┌───────────────────────────────────┐
│  Plotly Express/Graph Objects     │
│                                   │
│  fig_events = px.bar(events_df)   │
│  fig_geo = px.pie(geo_df)         │
│  fig_category = go.Figure(...)    │
└────────────┬──────────────────────┘
             │
             ↓ Return to Layout
        Dashboard Updates
        (charts re-render)
        │
        ↓ (waits 30 seconds)
        Auto-refresh triggers again
```

---

## 5. Loyalty Points Flow

```
User makes purchase of ₹2,500

        │
        ↓
┌───────────────────────────────────┐
│  Checkout Process                 │
│  (Future implementation)          │
│                                   │
│  Calculate points:                │
│  points = amount * POINTS_PER_RUPEE│
│  points = 2500 * 1 = 2,500 points │
└────────────┬──────────────────────┘
             │
             ↓ Add Points
POST /loyalty/api/add-points
        │
        ↓
┌───────────────────────────────────┐
│  loyalty_bp.add_points()          │
│  in routes/loyalty.py             │
│                                   │
│  1. Validate user_id              │
│  2. Get loyalty account           │
└────────────┬──────────────────────┘
             │
             ↓ Update Account
┌───────────────────────────────────┐
│  LoyaltyAccount.add_points(2500)  │
│  in models/user.py                │
│                                   │
│  1. points_balance += 2500        │
│  2. lifetime_points += 2500       │
│  3. Call update_tier()            │
└────────────┬──────────────────────┘
             │
             ↓ Check Tier Upgrade
┌───────────────────────────────────┐
│  LoyaltyAccount.update_tier()     │
│                                   │
│  if lifetime_points >= 10000:     │
│      tier = 'platinum'            │
│  elif lifetime_points >= 5000:    │
│      tier = 'gold'                │
│  elif lifetime_points >= 1000:    │
│      tier = 'silver'              │
│  else:                            │
│      tier = 'bronze'              │
└────────────┬──────────────────────┘
             │
             ↓ Commit Changes
┌───────────────────────────────────┐
│  Database Update                  │
│                                   │
│  UPDATE loyalty_accounts          │
│  SET points_balance = 5000,       │
│      lifetime_points = 5000,      │
│      tier = 'gold',               │
│      updated_at = now()           │
│  WHERE user_id = 1                │
└────────────┬──────────────────────┘
             │
             ↓ Return Updated Data
        {
          points_balance: 5000,
          tier: 'gold',
          next_tier: 'platinum',
          points_to_next_tier: 5000
        }
```

---

## 6. Data Ingestion Flow

```
User runs: python ingest_data.py --csv data/cosmetics.csv

        │
        ↓
┌───────────────────────────────────┐
│  ingest_data.py: ingest_csv()     │
│                                   │
│  1. Check if CSV file exists      │
└────────────┬──────────────────────┘
             │
             ↓ Read CSV
┌───────────────────────────────────┐
│  Pandas: pd.read_csv()            │
│                                   │
│  DataFrame with columns:          │
│  Brand, Label, Category, Price... │
└────────────┬──────────────────────┘
             │
             ↓ Process Rows
┌───────────────────────────────────┐
│  For each row in DataFrame:       │
│                                   │
│  1. Map columns flexibly          │
│     (Brand/brand → brand)         │
│                                   │
│  2. Clean price data              │
│     remove '$', '₹', commas       │
│                                   │
│  3. Convert USD to INR            │
│     price_inr = price * 83        │
│                                   │
│  4. Handle missing values         │
│     rating, ingredients, etc.     │
└────────────┬──────────────────────┘
             │
             ↓ Create Model Objects
┌───────────────────────────────────┐
│  Product objects creation         │
│                                   │
│  product = Product(               │
│      brand='Himalaya',            │
│      label='Face Cream',          │
│      category='Skincare',         │
│      price=12.99,                 │
│      price_inr=1078.17,          │
│      rating=4.5,                  │
│      ...                          │
│  )                                │
│  db.session.add(product)          │
└────────────┬──────────────────────┘
             │
             ↓ Batch Commit (every 100 rows)
┌───────────────────────────────────┐
│  db.session.commit()              │
│                                   │
│  INSERT INTO products VALUES (...) │
│  (100 rows at a time)             │
└────────────┬──────────────────────┘
             │
             ↓ Final Commit
┌───────────────────────────────────┐
│  All products inserted            │
│                                   │
│  Print statistics:                │
│  ✅ Imported: 500 products        │
│  ⚠️  Skipped: 10 rows (errors)    │
└───────────────────────────────────┘
```

---

## 7. Session Management Flow

```
User opens website for first time

        │ No session cookie
        ↓
┌───────────────────────────────────┐
│  @app.before_request              │
│  in app.py                        │
│                                   │
│  Check: 'session_id' in session?  │
│  → NO                             │
└────────────┬──────────────────────┘
             │
             ↓ Generate UUID
┌───────────────────────────────────┐
│  import uuid                      │
│  session['session_id'] = str(     │
│      uuid.uuid4()                 │
│  )                                │
│  → 'abc-123-def-456'              │
└────────────┬──────────────────────┘
             │
             ↓ Set Cookie
        Browser receives session cookie
        (encrypted, signed by Flask)
        │
        ↓
    Subsequent requests include session_id
        │
        ↓
┌───────────────────────────────────┐
│  All telemetry events tagged with │
│  this session_id for tracking     │
└───────────────────────────────────┘
```

---

## 8. Product Filtering Flow

```
User selects: Category = "Skincare", Min Price = 1000

        │ Form submission
        ↓
GET /products?category=Skincare&min_price=1000

        │
        ↓
┌───────────────────────────────────┐
│  products_bp.index()              │
│                                   │
│  brand = request.args.get('brand')│
│  → None                           │
│                                   │
│  category = request.args.get(     │
│      'category'                   │
│  ) → 'Skincare'                   │
│                                   │
│  min_price = request.args.get(    │
│      'min_price', type=float      │
│  ) → 1000.0                       │
└────────────┬──────────────────────┘
             │
             ↓ Build Query
┌───────────────────────────────────┐
│  Product.filter_products(         │
│      brand=None,                  │
│      category='Skincare',         │
│      min_price=1000.0,            │
│      max_price=None,              │
│      min_rating=None              │
│  )                                │
└────────────┬──────────────────────┘
             │
             ↓ SQLAlchemy Query
┌───────────────────────────────────┐
│  query = Product.query            │
│      .filter_by(is_active=True)   │
│                                   │
│  if category:                     │
│      query = query.filter(        │
│          Product.category ==      │
│          'Skincare'               │
│      )                            │
│                                   │
│  if min_price:                    │
│      query = query.filter(        │
│          Product.price_inr >= 1000│
│      )                            │
└────────────┬──────────────────────┘
             │
             ↓ Execute & Paginate
┌───────────────────────────────────┐
│  pagination = query.paginate(     │
│      page=1,                      │
│      per_page=12,                 │
│      error_out=False              │
│  )                                │
│                                   │
│  products = pagination.items      │
│  → [Product(id=1), ...]           │
└────────────┬──────────────────────┘
             │
             ↓ Render Template
        templates/products/index.html
        (displays filtered products)
```

---

## 9. Template Inheritance Flow

```
Browser requests: /products/5 (Product Detail)

        │
        ↓
┌───────────────────────────────────┐
│  Flask renders:                   │
│  templates/products/detail.html   │
└────────────┬──────────────────────┘
             │
             ↓ Extends Base
┌───────────────────────────────────┐
│  {% extends "base.html" %}        │
│                                   │
│  Loads: templates/base.html       │
└────────────┬──────────────────────┘
             │
             ↓ Base Template Structure
┌───────────────────────────────────┐
│  base.html:                       │
│                                   │
│  <!DOCTYPE html>                  │
│  <head>                           │
│      Tailwind CSS                 │
│      Google Fonts                 │
│      {% block extra_head %}       │
│  </head>                          │
│  <body>                           │
│      <nav> ... </nav>             │
│      {% block content %}          │
│          ← detail.html inserts    │
│      {% endblock %}               │
│      <footer> ... </footer>       │
│      {% block extra_js %}         │
│  </body>                          │
└────────────┬──────────────────────┘
             │
             ↓ Child Overrides Blocks
┌───────────────────────────────────┐
│  detail.html:                     │
│                                   │
│  {% block title %}                │
│      {{ product.label }}          │
│  {% endblock %}                   │
│                                   │
│  {% block content %}              │
│      <h1>{{ product.label }}</h1> │
│      <p>{{ product.description }}</p>│
│      ...                          │
│  {% endblock %}                   │
│                                   │
│  {% block extra_js %}             │
│      <script>addToCart(...)...</script>│
│  {% endblock %}                   │
└────────────┬──────────────────────┘
             │
             ↓ Final HTML Output
        Complete page with:
        - Navigation from base.html
        - Product content from detail.html
        - Footer from base.html
        - Custom JS from detail.html
```

---

## 10. Error Handling Flow

```
User requests: /products/9999 (doesn't exist)

        │
        ↓
┌───────────────────────────────────┐
│  products_bp.detail(9999)         │
│                                   │
│  product = Product.query.get_or_404(9999)│
│                                   │
│  → Product not found!             │
└────────────┬──────────────────────┘
             │
             ↓ Flask raises 404
┌───────────────────────────────────┐
│  @app.errorhandler(404)           │
│  in app.py                        │
│                                   │
│  return render_template(          │
│      'errors/404.html'            │
│  ), 404                           │
└────────────┬──────────────────────┘
             │
             ↓ Render Error Page
┌───────────────────────────────────┐
│  templates/errors/404.html        │
│                                   │
│  Displays:                        │
│  - "404" large text               │
│  - "Page Not Found" message       │
│  - "Return Home" button           │
└────────────┬──────────────────────┘
             │
             ↓ HTTP Response
        Status: 404 Not Found
        Content: Custom error page
```

---

## Key Takeaways

### Data Flows Through:
1. **Request** → Routes → Models → Database → Models → Templates → **Response**
2. **User Action** → JavaScript → API → Telemetry Model → Database
3. **Analytics** → Dash Callback → Database Queries → Pandas → Plotly → **Charts**

### Session Tracking:
- Every request has a session_id
- Telemetry events tagged with session
- Enables user behavior analysis

### Database Central:
- All data persisted in SQLite (dev)
- SQLAlchemy ORM abstracts SQL
- Models encapsulate business logic

---

**Document Version:** 1.0  
**Last Updated:** January 2026
