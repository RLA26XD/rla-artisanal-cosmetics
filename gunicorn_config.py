"""
Gunicorn configuration for RLA Artisanal Cosmetics
Production WSGI server configuration
"""
import multiprocessing

# Server socket
bind = "0.0.0.0:6969"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after N requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "rla_cosmetics"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("\n" + "="*60)
    print("  Gunicorn starting...")
    print("="*60 + "\n")

def when_ready(server):
    """Called just after the server is started."""
    print("✓ Gunicorn workers ready")
    print(f"✓ Listening on {bind}")
    print(f"✓ Workers: {workers}")
    print("="*60 + "\n")

# SSL (uncomment for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
