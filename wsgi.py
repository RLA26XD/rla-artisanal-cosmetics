"""
WSGI entry point for production deployment
"""
import os
from app import create_app

# Determine environment
env = os.environ.get('FLASK_ENV', 'production')

# Create application instance
app = create_app(env)

if __name__ == "__main__":
    app.run()
