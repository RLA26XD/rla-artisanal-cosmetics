"""
Product-related routes for browsing, filtering, and viewing products
"""
from flask import Blueprint, render_template, request, session, jsonify
from models import db
from models.product import Product
from models.telemetry import Telemetry
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
def index():
    """
    Product listing page with filters for Brand and Category.
    """
    # Get filter parameters
    brand = request.args.get('brand', None)
    category = request.args.get('category', None)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)
    
    # Build query with filters
    query = Product.filter_products(
        brand=brand,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating
    )
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 12
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    
    # Get all brands and categories for filters
    brands = [brand[0] for brand in Product.get_all_brands()]
    categories = [cat[0] for cat in Product.get_all_categories()]
    
    # Log category click if category filter is applied
    if category:
        Telemetry.log_event(
            event_type='category_click',
            category=category,
            session_id=session.get('session_id')
        )
    
    return render_template(
        'products/index.html',
        products=products,
        pagination=pagination,
        brands=brands,
        categories=categories,
        selected_brand=brand,
        selected_category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating
    )


@products_bp.route('/<int:product_id>')
def detail(product_id):
    """
    Product detail page showing full information.
    """
    product = Product.query.get_or_404(product_id)
    
    # Log product view
    Telemetry.log_event(
        event_type='product_view',
        product_id=product_id,
        session_id=session.get('session_id'),
        category=product.category
    )
    
    # Get related products from same category
    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product_id,
        Product.is_active == True
    ).limit(4).all()
    
    return render_template(
        'products/detail.html',
        product=product,
        related_products=related_products
    )


@products_bp.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    """
    Legacy API endpoint for cart addition - redirects to new cart system.
    Kept for backward compatibility.
    """
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'error': 'Product ID required'}), 400
    
    # Forward to new cart endpoint
    from routes.cart import cart_bp
    from flask import current_app
    with current_app.test_request_context('/cart/add', method='POST', json=data):
        from routes.cart import add as cart_add
        return cart_add()


@products_bp.route('/api/cart-abandonment', methods=['POST'])
def cart_abandonment():
    """
    API endpoint to log cart abandonment event.
    Called when user leaves cart page without purchasing.
    """
    data = request.get_json()
    
    # Log cart abandonment
    Telemetry.log_event(
        event_type='cart_abandonment',
        session_id=session.get('session_id'),
        event_data=data.get('reason', 'unknown'),
        geo_state=data.get('geo_state'),
        geo_city=data.get('geo_city')
    )
    
    return jsonify({'success': True, 'message': 'Event logged'})


@products_bp.route('/search')
def search():
    """
    Product search functionality.
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('products.index'))
    
    # Search in product label, brand, and category
    products = Product.query.filter(
        db.or_(
            Product.label.ilike(f'%{query}%'),
            Product.brand.ilike(f'%{query}%'),
            Product.category.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        ),
        Product.is_active == True
    ).all()
    
    # Log search event
    Telemetry.log_event(
        event_type='search',
        search_term=query,
        session_id=session.get('session_id')
    )
    
    # Use products index template but pass search query
    return render_template(
        'products/index.html',
        products=products,
        pagination=None,
        brands=[],
        categories=[],
        selected_brand=None,
        selected_category=None,
        min_price=None,
        max_price=None,
        min_rating=None,
        search_query=query
    )
