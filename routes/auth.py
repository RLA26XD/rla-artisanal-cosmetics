"""
Authentication routes for user login, registration, and logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User, LoyaltyAccount
from models.telemetry import Telemetry
from utils.helpers import get_or_create_session_id
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    """Validate Indian phone number format."""
    # Remove spaces and dashes
    phone = phone.replace(' ', '').replace('-', '')
    # Check if it's 10 digits or starts with +91
    return (len(phone) == 10 and phone.isdigit()) or \
           (len(phone) == 13 and phone.startswith('+91') and phone[3:].isdigit())


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            
            # Log login event
            Telemetry.log_event(
                event_type='user_login',
                session_id=get_or_create_session_id(),
                event_data=f'user:{user.id}'
            )
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation
        errors = []
        
        if not email or not is_valid_email(email):
            errors.append('Valid email is required')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if not name or len(name) < 2:
            errors.append('Name is required')
        
        if phone and not is_valid_phone(phone):
            errors.append('Invalid phone number format')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            email=email,
            name=name,
            phone=phone
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create loyalty account
        loyalty_account = LoyaltyAccount(user_id=user.id)
        db.session.add(loyalty_account)
        db.session.commit()
        
        # Log registration event
        Telemetry.log_event(
            event_type='user_registration',
            session_id=get_or_create_session_id(),
            event_data=f'user:{user.id}'
        )
        
        # Auto-login after registration
        login_user(user)
        
        flash('Account created successfully! Welcome to RLA Cosmetics!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user."""
    # Log logout event
    Telemetry.log_event(
        event_type='user_logout',
        session_id=get_or_create_session_id(),
        event_data=f'user:{current_user.id}'
    )
    
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    pincode = request.form.get('pincode', '').strip()
    
    # Validation
    errors = []
    
    if not name or len(name) < 2:
        errors.append('Name is required')
    
    if phone and not is_valid_phone(phone):
        errors.append('Invalid phone number format')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('auth.profile'))
    
    # Update user
    current_user.name = name
    current_user.phone = phone
    current_user.address = address
    current_user.city = city
    current_user.state = state
    current_user.pincode = pincode
    
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))
