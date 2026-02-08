"""
Main Flask Application with Dash Integration
RLA Artisanal Cosmetics E-Commerce Platform
"""
import os
import warnings
from flask import Flask, render_template, request, session, jsonify
from flask_login import LoginManager
from config import config
from models import db
from models.product import Product
from models.telemetry import Telemetry
from models.user import User, LoyaltyAccount

# Suppress specific warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='plotly')
warnings.filterwarnings('ignore', category=FutureWarning, message='.*length-1 list-like.*')


def init_database():
    """
    Initialize database tables and import products from CSV if needed.
    This runs on app startup to ensure the database is ready.
    """
    import pandas as pd
    from pathlib import Path
    
    # Create all tables
    db.create_all()
    print("✅ Database tables created")
    
    # Check if products exist
    if Product.query.first() is None:
        print("📦 No products found. Importing from CSV...")
        
        # Import products from CSV
        csv_path = Path(__file__).parent / 'data' / 'cosmetics.csv'
        
        if csv_path.exists():
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding, on_bad_lines='skip')
                    print(f"✓ Loaded CSV with {encoding} encoding")
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            
            if df is None:
                # Last resort: read with errors='ignore'
                df = pd.read_csv(csv_path, encoding='utf-8', errors='ignore', on_bad_lines='skip')
            
            # Import products
            products = []
            for _, row in df.iterrows():
                # Handle price - use 0.0 as default if missing
                price_val = row.get('price', 0)
                if pd.isna(price_val) or price_val == '':
                    price_val = 0.0
                else:
                    try:
                        price_val = float(price_val)
                    except (ValueError, TypeError):
                        price_val = 0.0
                
                product = Product(
                    label=row.get('product_name', '') or row.get('Label', ''),
                    brand=row.get('brand', '') or row.get('Brand', ''),
                    category=row.get('category', '') or row.get('Category', ''),
                    price=price_val,
                    price_inr=price_val * 83 if price_val > 0 else 0.0,
                    rating=float(row.get('rating', 0)) if pd.notna(row.get('rating')) else None,
                    ingredients=row.get('ingredients', '') or row.get('Ingredients', '')
                )
                products.append(product)
                
                # Batch commit every 1000 products
                if len(products) >= 1000:
                    db.session.bulk_save_objects(products)
                    db.session.commit()
                    products = []
            
            # Commit remaining products
            if products:
                db.session.bulk_save_objects(products)
                db.session.commit()
            
            print(f"✓ Imported {df.shape[0]} products from CSV")
        else:
            print(f"⚠️  CSV file not found at {csv_path}")


def create_app(config_name='development'):
    """
    Application factory pattern for creating Flask app.
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize Dash analytics dashboard
    init_dash(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize database on first startup
    with app.app_context():
        init_database()
    
    # Before request handler for session management
    @app.before_request
    def before_request():
        """Initialize session variables."""
        if 'session_id' not in session:
            import uuid
            session['session_id'] = str(uuid.uuid4())
    
    return app


def register_blueprints(app):
    """Register Flask blueprints for route organization."""
    from routes.main import main_bp
    from routes.products import products_bp
    from routes.loyalty import loyalty_bp
    from routes.cart import cart_bp
    from routes.auth import auth_bp
    from routes.health import health_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(loyalty_bp, url_prefix='/loyalty')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(health_bp)


def init_dash(app):
    """
    Initialize Dash analytics dashboard and integrate with Flask.
    The Dash app runs on /admin/analytics route.
    """
    import dash
    from dash import dcc, html, Input, Output
    import dash_bootstrap_components as dbc
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    from datetime import datetime, timedelta, timezone
    
    # Create Dash app with Flask server
    dash_app = dash.Dash(
        __name__,
        server=app,
        url_base_pathname='/admin/analytics/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    
    # Dash Layout
    dash_app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("RLA Cosmetics Analytics Dashboard", 
                       className="text-center mb-4",
                       style={'color': '#022D1F', 'fontWeight': 'bold'}),
                html.Hr()
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Cart Abandonment Rate", className="card-title"),
                        html.H2(id="abandonment-rate", className="text-danger")
                    ])
                ], className="mb-4")
            ], width=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Events (24h)", className="card-title"),
                        html.H2(id="total-events", className="text-primary")
                    ])
                ], className="mb-4")
            ], width=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Products", className="card-title"),
                        html.H2(id="total-products", className="text-success")
                    ])
                ], className="mb-4")
            ], width=4),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='events-by-type')
            ], width=6),
            
            dbc.Col([
                dcc.Graph(id='geo-distribution')
            ], width=6),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='category-performance')
            ], width=12),
        ]),
        
        # Auto-refresh interval (every 30 seconds)
        dcc.Interval(
            id='interval-component',
            interval=30*1000,  # in milliseconds
            n_intervals=0
        )
        
    ], fluid=True, style={'padding': '20px'})
    
    # Callbacks for real-time data updates
    @dash_app.callback(
        [Output('abandonment-rate', 'children'),
         Output('total-events', 'children'),
         Output('total-products', 'children'),
         Output('events-by-type', 'figure'),
         Output('geo-distribution', 'figure'),
         Output('category-performance', 'figure')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_dashboard(n):
        """Update all dashboard components."""
        with app.app_context():
            # KPI Metrics
            abandonment_rate = f"{Telemetry.get_cart_abandonment_rate(days=30):.1f}%"
            
            # Total events in last 24 hours
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            total_events = db.session.query(Telemetry).filter(
                Telemetry.timestamp >= yesterday
            ).count()
            
            total_products = db.session.query(Product).filter_by(is_active=True).count()
            
            # Events by Type Chart
            events_data = db.session.query(
                Telemetry.event_type,
                db.func.count(Telemetry.id).label('count')
            ).group_by(Telemetry.event_type).all()
            
            if events_data:
                events_df = pd.DataFrame(events_data, columns=['event_type', 'count'])
                fig_events = px.bar(
                    events_df, 
                    x='event_type', 
                    y='count',
                    title='Events by Type',
                    color='event_type',
                    color_discrete_sequence=['#022D1F', '#F4C430', '#1f77b4', '#ff7f0e']
                )
                fig_events.update_layout(showlegend=False)
            else:
                fig_events = go.Figure()
                fig_events.add_annotation(text="No data available", showarrow=False)
            
            # Geographic Distribution
            geo_data = Telemetry.get_top_states(limit=10)
            if geo_data:
                geo_df = pd.DataFrame(geo_data, columns=['state', 'count'])
                fig_geo = px.pie(
                    geo_df,
                    values='count',
                    names='state',
                    title='Top 10 States by Activity',
                    color_discrete_sequence=px.colors.sequential.Emrld
                )
            else:
                fig_geo = go.Figure()
                fig_geo.add_annotation(text="No geographic data available", showarrow=False)
            
            # Category Performance
            category_data = db.session.query(
                Product.category,
                db.func.count(Product.id).label('product_count'),
                db.func.avg(Product.rating).label('avg_rating')
            ).filter(Product.is_active == True).group_by(Product.category).all()
            
            if category_data:
                cat_df = pd.DataFrame(category_data, 
                                     columns=['category', 'product_count', 'avg_rating'])
                fig_category = go.Figure()
                fig_category.add_trace(go.Bar(
                    x=cat_df['category'],
                    y=cat_df['product_count'],
                    name='Product Count',
                    marker_color='#022D1F'
                ))
                fig_category.add_trace(go.Scatter(
                    x=cat_df['category'],
                    y=cat_df['avg_rating'],
                    name='Avg Rating',
                    yaxis='y2',
                    marker_color='#F4C430'
                ))
                fig_category.update_layout(
                    title='Category Performance',
                    yaxis=dict(title='Product Count'),
                    yaxis2=dict(title='Average Rating', overlaying='y', side='right'),
                    legend=dict(x=0.01, y=0.99)
                )
            else:
                fig_category = go.Figure()
                fig_category.add_annotation(text="No category data available", showarrow=False)
            
            return abandonment_rate, str(total_events), str(total_products), \
                   fig_events, fig_geo, fig_category
    
    return dash_app


def register_error_handlers(app):
    """Register error handlers for common HTTP errors."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal error: {error}')
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}', exc_info=True)
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500


# Create the application instance (for gunicorn/wsgi)
# Only create if not being imported
if __name__ != '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'production'))
