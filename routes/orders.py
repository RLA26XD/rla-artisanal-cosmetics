"""
Order routes for checkout, order placement, and order management.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import db
from models.product import Product
from models.order import Order, OrderItem

orders = Blueprint('orders', __name__)


@orders.route('/checkout')
@login_required
def checkout():
    """Display checkout page with shipping form."""
    # Get cart from session
    cart = session.get('cart', {})
    
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.index'))
    
    # Calculate cart items and total
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price_inr * quantity
            cart_items.append({
                'id': product.id,
                'name': product.label,
                'brand': product.brand,
                'price': product.price_inr,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('checkout.html', cart_items=cart_items, total=total)


@orders.route('/checkout', methods=['POST'])
@login_required
def place_order():
    """Process order placement."""
    # Get cart from session
    cart = session.get('cart', {})
    
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.index'))
    
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    postal_code = request.form.get('postal_code')
    notes = request.form.get('notes', '')
    
    # Validate required fields
    if not all([name, email, phone, address, city, state, postal_code]):
        flash('Please fill in all required fields', 'danger')
        return redirect(url_for('orders.checkout'))
    
    # Calculate total
    total = 0
    order_items = []
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price_inr * quantity
            total += subtotal
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': product.price_inr,
                'subtotal': subtotal
            })
    
    # Generate unique order number
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{Order.query.count() + 1:04d}"
    
    # Create order
    order = Order(
        order_number=order_number,
        user_id=current_user.id,
        status='pending',
        total_amount=total,
        shipping_name=name,
        shipping_email=email,
        shipping_phone=phone,
        shipping_address=address,
        shipping_city=city,
        shipping_state=state,
        shipping_postal_code=postal_code,
        notes=notes
    )
    
    db.session.add(order)
    db.session.flush()  # Get order ID
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data['product'].id,
            product_name=item_data['product'].label,
            product_brand=item_data['product'].brand,
            price=item_data['price'],
            quantity=item_data['quantity'],
            subtotal=item_data['subtotal']
        )
        db.session.add(order_item)
    
    # Commit transaction
    try:
        db.session.commit()
        
        # Clear cart
        session.pop('cart', None)
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('orders.order_confirmation', order_id=order.id))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while placing your order. Please try again.', 'danger')
        return redirect(url_for('orders.checkout'))


@orders.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Display order confirmation page."""
    order = Order.query.get_or_404(order_id)
    
    # Ensure user can only see their own orders
    if order.user_id != current_user.id:
        flash('Order not found', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('order_confirmation.html', order=order)


@orders.route('/account')
@login_required
def account():
    """Display user account dashboard with orders."""
    # Get user's orders
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc()).all()
    
    return render_template('account.html', orders=orders)


@orders.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """Display detailed order information."""
    order = Order.query.get_or_404(order_id)
    
    # Ensure user can only see their own orders
    if order.user_id != current_user.id:
        flash('Order not found', 'danger')
        return redirect(url_for('orders.account'))
    
    return render_template('order_detail.html', order=order)


@orders.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information."""
    username = request.form.get('username')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Update username
    if username and username != current_user.username:
        # Check if username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already taken', 'danger')
            return redirect(url_for('orders.account'))
        
        current_user.username = username
    
    # Update password if provided
    if current_password and new_password:
        # Verify current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('orders.account'))
        
        # Verify password confirmation
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('orders.account'))
        
        # Update password
        current_user.set_password(new_password)
    
    try:
        db.session.commit()
        flash('Profile updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating your profile', 'danger')
    
    return redirect(url_for('orders.account'))
