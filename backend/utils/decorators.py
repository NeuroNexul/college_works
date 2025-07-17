from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


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
