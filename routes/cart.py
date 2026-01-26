"""
Shopping cart routes for managing cart items
"""
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from models.product import Product
from models.telemetry import Telemetry
from utils.helpers import get_or_create_session_id

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


def get_cart():
    """Get cart items from session."""
    return session.get('cart', {})


def save_cart(cart):
    """Save cart to session."""
    session['cart'] = cart
    session.modified = True


def calculate_cart_totals(cart_items):
    """Calculate cart subtotal, tax, and total."""
    subtotal = sum(item['quantity'] * item['price'] for item in cart_items)
    tax_rate = 0.18  # 18% GST for India
    tax = subtotal * tax_rate
    total = subtotal + tax
    
    return {
        'subtotal': round(subtotal, 2),
        'tax': round(tax, 2),
        'total': round(total, 2),
        'item_count': sum(item['quantity'] for item in cart_items)
    }


@cart_bp.route('/')
def index():
    """Display shopping cart page."""
    cart = get_cart()
    cart_items = []
    
    # Fetch product details for each cart item
    for product_id, item_data in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            cart_items.append({
                'product': product,
                'quantity': item_data['quantity'],
                'price': product.price_inr,
                'subtotal': product.price_inr * item_data['quantity']
            })
    
    totals = calculate_cart_totals(cart_items)
    
    # Log cart view
    Telemetry.log_event(
        event_type='page_view',
        session_id=get_or_create_session_id(),
        event_data='cart'
    )
    
    return render_template('cart/index.html', cart_items=cart_items, totals=totals)


@cart_bp.route('/add', methods=['POST'])
def add():
    """Add item to cart (handles both JSON and form data)."""
    # Handle JSON requests
    if request.is_json:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
    else:
        # Handle form submissions
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
    
    if not product_id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Product ID required'}), 400
        flash('Product ID required', 'error')
        return redirect(url_for('products.index'))
    
    # Validate product exists
    product = Product.query.get(int(product_id))
    if not product or not product.is_active:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        flash('Product not found', 'error')
        return redirect(url_for('products.index'))
    
    # Get cart and add/update item
    cart = get_cart()
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += int(quantity)
    else:
        from datetime import datetime, timezone
        cart[product_id_str] = {
            'quantity': int(quantity),
            'added_at': datetime.now(timezone.utc).isoformat()
        }
    
    save_cart(cart)
    
    # Log cart addition
    Telemetry.log_event(
        event_type='cart_addition',
        product_id=int(product_id),
        session_id=get_or_create_session_id(),
        category=product.category
    )
    
    if request.is_json:
        cart_count = sum(item['quantity'] for item in cart.values())
        return jsonify({
            'success': True, 
            'message': f'{product.label} added to cart',
            'cart_count': cart_count
        })
    
    flash(f'{product.label} added to cart!', 'success')
    return redirect(request.referrer or url_for('products.index'))


@cart_bp.route('/update/<int:product_id>', methods=['POST'])
def update(product_id):
    """Update cart item quantity."""
    quantity = request.form.get('quantity', type=int)
    
    if not quantity or quantity < 1:
        flash('Invalid quantity', 'error')
        return redirect(url_for('cart.index'))
    
    cart = get_cart()
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str]['quantity'] = quantity
        save_cart(cart)
        flash('Cart updated', 'success')
    else:
        flash('Item not in cart', 'error')
    
    return redirect(url_for('cart.index'))


@cart_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove(product_id):
    """Remove item from cart."""
    cart = get_cart()
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        save_cart(cart)
        
        # Log cart removal
        Telemetry.log_event(
            event_type='cart_removal',
            product_id=product_id,
            session_id=get_or_create_session_id()
        )
        
        flash('Item removed from cart', 'success')
    else:
        flash('Item not in cart', 'error')
    
    return redirect(url_for('cart.index'))


@cart_bp.route('/clear', methods=['POST'])
def clear():
    """Clear entire cart."""
    session.pop('cart', None)
    flash('Cart cleared', 'success')
    return redirect(url_for('cart.index'))


@cart_bp.route('/count')
def count():
    """Get cart item count (API endpoint for navbar)."""
    cart = get_cart()
    count = sum(item['quantity'] for item in cart.values())
    return jsonify({'count': count})
