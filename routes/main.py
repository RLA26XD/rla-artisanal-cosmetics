"""
Main routes for homepage and general pages
"""
from flask import Blueprint, render_template, session
from models.product import Product
from models.telemetry import Telemetry
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

# Category mappings for display
CATEGORY_GROUPS = {
    'skincare': ['skincare'],
    'makeup': ['face', 'lips', 'eyes'],
    'body': ['body'],
    'hair': ['hair']
}


@main_bp.route('/')
def index():
    """
    Landing page with featured products and hero section.
    Highlights Skincare and Makeup categories.
    """
    # Log page view
    Telemetry.log_event(
        event_type='page_view',
        session_id=session.get('session_id'),
        event_data='homepage'
    )
    
    # Get featured skincare products (high rating)
    skincare_products = Product.query.filter(
        Product.category.in_(CATEGORY_GROUPS['skincare']),
        Product.is_active == True,
        Product.rating >= 4.0
    ).order_by(Product.rating.desc()).limit(6).all()
    
    # Get featured makeup products (high rating)
    makeup_products = Product.query.filter(
        Product.category.in_(CATEGORY_GROUPS['makeup']),
        Product.is_active == True,
        Product.rating >= 4.0
    ).order_by(Product.rating.desc()).limit(6).all()
    
    # Get all unique categories for navigation
    all_categories = [cat[0] for cat in Product.get_all_categories()]
    
    return render_template(
        'index.html',
        skincare_products=skincare_products,
        makeup_products=makeup_products,
        categories=all_categories
    )


@main_bp.route('/about')
def about():
    """About page for brand story."""
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')


@main_bp.route('/contact', methods=['POST'])
def contact_submit():
    """Handle contact form submission."""
    from flask import flash, redirect, url_for, request
    
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    # In a real application, you would send an email or save to database
    # For now, just show a success message
    flash(f'Thank you {name}! We have received your message and will get back to you soon.', 'success')
    return redirect(url_for('main.contact'))


@main_bp.route('/privacy')
def privacy():
    """Privacy policy page."""
    return render_template('privacy.html')


@main_bp.route('/terms')
def terms():
    """Terms and conditions page."""
    return render_template('terms.html')
