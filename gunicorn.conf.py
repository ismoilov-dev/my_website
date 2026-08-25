import multiprocessing
import os

# Gunicorn Production Configuration
bind = "127.0.0.1:8000"
# If using UNIX socket: bind = "unix:/run/blog.sock"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5

# Logging settings
accesslog = "-"  # stdout or log file path e.g. "/var/log/gunicorn/access.log"
errorlog = "-"   # stderr or log file path e.g. "/var/log/gunicorn/error.log"
loglevel = "info"
capture_output = True
