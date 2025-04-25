from datetime import datetime
import logging

def timestamp():
    """Return the current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
