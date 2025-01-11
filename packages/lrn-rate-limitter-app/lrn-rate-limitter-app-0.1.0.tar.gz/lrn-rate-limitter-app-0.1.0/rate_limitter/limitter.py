import time
import json
import logging
from functools import wraps
from collections import defaultdict
from azure.functions import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)
# In-memory rate limit tracker
request_counts = defaultdict(lambda: defaultdict(list))

def rate_limit(rate_limit=5, time_window=60):
    """
    Rate limiter decorator to limit the number of requests per client to an endpoint.

    Args:
        rate_limit (int): Maximum number of requests allowed.
        time_window (int): Time window in seconds for the rate limit.

    Returns:
        Wrapper function to enforce rate limits.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(req, *args, **kwargs):
            try:
                # Identify client using Authorization header or fallback to "anonymous"
                client_id = req.headers.get("Authorization", "anonymous")
                endpoint = func.__name__  # Use the function name as endpoint identifier
                
                current_time = time.time()
                request_times = request_counts[client_id][endpoint]

                # Clean up outdated requests outside the time window
                request_counts[client_id][endpoint] = [
                    t for t in request_times if current_time - t <= time_window
                ]

                # Check if the rate limit is exceeded
                if len(request_counts[client_id][endpoint]) >= rate_limit:
                    retry_after = time_window - (current_time - request_counts[client_id][endpoint][0])
                    return HttpResponse(
                        json.dumps({
                            "error": "Rate limit exceeded. Please try again later.",
                            "retry_after_seconds": round(retry_after, 2)
                        }),
                        status_code=429,
                        mimetype="application/json"
                    )

                # Log the current request timestamp
                request_counts[client_id][endpoint].append(current_time)

                # Proceed with the decorated function
                return func(req, *args, **kwargs)
            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                return HttpResponse(
                    json.dumps({"error": "Internal server error occurred in rate limiting."}),
                    status_code=500,
                    mimetype="application/json"
                )
        return wrapper
    return decorator
