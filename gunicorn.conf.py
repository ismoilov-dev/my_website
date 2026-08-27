import multiprocessing
import os

# Gunicorn configuration for the systemd service behind nginx.

# Loopback only: nginx is the sole entry point, so gunicorn must not be
# reachable from the internet on port 8000.
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:8000")

# Number of worker processes
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1 if hasattr(multiprocessing, 'cpu_count') else 3))

# Number of threads per worker process
threads = int(os.environ.get("GUNICORN_THREADS", "2"))

# Worker timeout in seconds
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "60"))

# Keep-alive connection timeout
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# Logging settings
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")

# Preload application code before worker processes are forked
preload_app = True
