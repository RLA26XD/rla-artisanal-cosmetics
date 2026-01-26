"""
Main routes for homepage and general pages
"""
from flask import Blueprint, render_template, session
from models.product import Product
from models.telemetry import Telemetry

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Landing page with featured products and hero section.
    Highlights Skincare and Face Makeup categories.
    """
    # Log page view
    Telemetry.log_event(
        event_type='page_view',
        session_id=session.get('session_id'),
        event_data='homepage'
    )
    
    # Get featured products from Skincare and Face Makeup
    skincare_products = Product.query.filter_by(
        category='Skincare', 
        is_active=True
    ).order_by(Product.rating.desc()).limit(6).all()
    
    makeup_products = Product.query.filter_by(
        category='Face Makeup', 
        is_active=True
    ).order_by(Product.rating.desc()).limit(6).all()
    
    # Get all categories for navigation
    categories = [cat[0] for cat in Product.get_all_categories()]
    
    return render_template(
        'index.html',
        skincare_products=skincare_products,
        makeup_products=makeup_products,
        categories=categories
    )


@main_bp.route('/about')
def about():
    """About page for brand story."""
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')
