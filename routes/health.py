"""
Health check endpoint for monitoring
"""
from flask import jsonify, Blueprint
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    from models import db
    from models.product import Product
    
    try:
        # Check database connectivity
        product_count = Product.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'products': product_count,
            'environment': os.getenv('FLASK_ENV', 'unknown')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'environment': os.getenv('FLASK_ENV', 'unknown')
        }), 500

@health_bp.route('/debug-info')
def debug_info():
    """Debug information endpoint (disable in production)"""
    import sys
    from flask import current_app
    
    # Only allow in development
    if os.getenv('FLASK_ENV') == 'production':
        return jsonify({'error': 'Not available in production'}), 403
    
    return jsonify({
        'python_version': sys.version,
        'database_uri': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set'),
        'secret_key_set': bool(current_app.config.get('SECRET_KEY')),
        'debug_mode': current_app.debug,
        'environment': os.getenv('FLASK_ENV'),
        'cwd': os.getcwd(),
        'instance_path': current_app.instance_path
    }), 200
