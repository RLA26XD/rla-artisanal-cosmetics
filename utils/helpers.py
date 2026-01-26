"""
Utility functions for the RLA Artisanal Cosmetics application
"""
from functools import wraps
from flask import session, redirect, url_for, request
import uuid


def generate_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def get_or_create_session_id():
    """Get existing session ID or create a new one."""
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
    return session['session_id']


def detect_device_type(user_agent_string):
    """
    Detect device type from user agent string.
    
    Args:
        user_agent_string: Browser user agent string
        
    Returns:
        String: 'mobile', 'tablet', or 'desktop'
    """
    if not user_agent_string:
        return 'unknown'
    
    user_agent = user_agent_string.lower()
    
    if 'mobile' in user_agent or 'android' in user_agent:
        return 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        return 'tablet'
    else:
        return 'desktop'


def format_currency(amount, currency='INR'):
    """
    Format currency amount with proper symbol.
    
    Args:
        amount: Numeric amount
        currency: Currency code (INR, USD)
        
    Returns:
        Formatted string
    """
    if currency == 'INR':
        return f"₹{amount:,.2f}"
    elif currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f}"


def calculate_loyalty_points(amount_spent):
    """
    Calculate loyalty points based on amount spent.
    
    Args:
        amount_spent: Amount in rupees
        
    Returns:
        Integer points earned
    """
    from config import Config
    return int(amount_spent * Config.POINTS_PER_RUPEE)


def login_required(f):
    """
    Decorator for routes that require authentication.
    For now, this is a placeholder for future implementation.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement proper authentication
        # For now, allow all access
        return f(*args, **kwargs)
    return decorated_function
