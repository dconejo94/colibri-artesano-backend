from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed by client IP; in-memory
limiter = Limiter(key_func=get_remote_address)
