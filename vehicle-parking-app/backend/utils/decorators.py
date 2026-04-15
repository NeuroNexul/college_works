from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import get_jwt, verify_jwt_in_request
import json
from datetime import timedelta


def admin_required():
    """
    A custom decorator that verifies the JWT is present and the user's role is 'admin'.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # First, verify that a valid JWT is present in the request
            verify_jwt_in_request()
            # Then, get the claims from the JWT
            claims = get_jwt()
            # Check if the role is 'admin'
            if claims.get("role") == "admin":
                # If the role is 'admin', proceed with the original function
                return fn(*args, **kwargs)
            else:
                # If the role is not 'admin', return a 403 Forbidden error
                return jsonify(message="Admins only!"), 403
        return decorator
    return wrapper


def cache(minutes=5):
    """
    A decorator to cache the result of a Flask route in Redis.
    The cache key is generated from the route's path and query string.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Get the Redis client from the Flask app context
            redis_client = current_app.redis_client

            # 2. Generate a unique cache key for this specific request
            # This ensures that '/api/lots' and '/api/lots?page=2' have different caches
            cache_key = request.full_path

            # 3. Try to get the cached result from Redis
            try:
                cached_result = redis_client.get(cache_key)
            except Exception as e:
                # If Redis is down, we don't want the app to crash.
                # Log the error and proceed as if there was a cache miss.
                print(f"Redis Error: Could not get from cache. {e}")
                cached_result = None

            # 4. If a cached result exists (cache hit)
            if cached_result:
                print(f"CACHE HIT for key: {cache_key}")
                # The result is stored as a JSON string, so we parse it back
                # and return it as a Flask JSON response.
                return jsonify(json.loads(cached_result))

            # 5. If no cached result exists (cache miss)
            print(f"CACHE MISS for key: {cache_key}")
            # Execute the original route function to get the fresh data
            fresh_result = f(*args, **kwargs)

            # The route returns a Response object. We get the JSON data from it.
            # We must handle cases where the route might not return JSON.
            # The result could be tuple, (response, status_code, headers)
            try:
                if isinstance(fresh_result, tuple):
                    data_to_cache = fresh_result[0].get_json()
                else:
                    data_to_cache = fresh_result.get_json()
            except Exception:
                print(f"Response is not JSON for key: {cache_key}")
                # If the response is not JSON, we can't cache it. Just return it.
                return fresh_result

            # 6. Store the fresh result in Redis with an expiration time
            try:
                # `ex` is the expiration time in seconds
                redis_client.setex(cache_key, int(timedelta(
                    minutes=minutes).total_seconds()), json.dumps(data_to_cache))
            except Exception as e:
                # Again, if Redis is down, just log it and move on.
                print(f"Redis Error: Could not set cache. {e}")

            return fresh_result
        return decorated_function
    return decorator
