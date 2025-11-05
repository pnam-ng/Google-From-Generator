"""
Gunicorn configuration for production deployment
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes - optimized for free tier (lightweight)
# Use fewer workers for free tier platforms
cpu_count = multiprocessing.cpu_count()
workers = min(cpu_count * 2 + 1, 2)  # Max 2 workers for free tier
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000  # Restart workers after 1000 requests
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'google-form-generator'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None

