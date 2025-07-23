# /backend/router/auth.py

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies

# Import your User model and the db instance
from db.models import User
from db.db import db

# The Blueprint you already have
bp = Blueprint("auth", __name__)


def create_admin_user():
    """
    Function to create an admin user if it doesn't exist.
    This is useful for setting up the initial admin user.
    """
    admin_email = "admin@nexul.in"
    admin_password = "admin@123"  # Change this to a secure password in production
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        try:
            new_admin = User(
                email=admin_email,
                full_name="Admin User",
                address="123 Admin St",
                pin_code="123456",
                role='admin'  # Set the role to 'admin'
            )
            new_admin.set_password(admin_password)  # Hash the password
            db.session.add(new_admin)
            db.session.commit()
            print("Admin user created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")
    else:
        print("Admin user already exists.")


@bp.route("/register", methods=["POST"])
def register_user():
    """
    Endpoint for user registration.
    """
    data = request.get_json()

    # Basic Validation
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400

    # Check if user already exists
    if User.query.filter_by(email=data.get('email')).first():
        # 409 Conflict
        return jsonify({"message": "This email is already registered"}), 409

    # Create New User
    try:
        new_user = User(
            email=data.get('email'),
            full_name=data.get('full_name'),
            address=data.get('address'),
            pin_code=data.get('pin_code'),
            role='user'  # Regular users can only register as 'user'
        )
        new_user.set_password(data.get('password'))  # Hash the password

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred during registration.", "error": str(e)}), 500


@bp.route("/login", methods=["POST"])
def login_user():
    """
    Endpoint for user and admin login.
    Returns a JWT access token upon successful authentication.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    # Get rememberMe flag from frontend
    remember_me = data.get('rememberMe', False)

    print(f"Login attempt for email: {email}, rememberMe: {remember_me}")

    # Basic Validation
    if not data or not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    print(f"User found: {user}")

    # Authenticate User
    # Check if user exists and password is correct
    if not user or not user.check_password(password):
        # 401 Unauthorized
        return jsonify({"message": "Invalid email or password"}), 401

    # Create JWT Token
    # We store the user's role in the JWT's claims for easy access on protected routes
    additional_claims = {"role": user.role}
    access_token = create_access_token(
        identity=str(user.id),  # The 'identity' of the token, usually user ID
        additional_claims=additional_claims
    )

    user_data = {
        "id": user.id,
        "email": user.email,
        "fullName": user.full_name,
        "role": user.role
    }

    if remember_me:
        # If "Remember Me" is true, set the token in a secure, HttpOnly cookie
        response = make_response(
            jsonify(user=user_data, msg="Login successful"))
        set_access_cookies(response, access_token,
                           max_age=60*60*24*30)  # 30 days
        return response, 200
    else:
        # Otherwise, return the token in the JSON body
        return jsonify(
            access_token=access_token,
            user=user_data
        ), 200

# Add a logout route to unset the cookie


@bp.route("/logout", methods=["POST"])
def logout_user():
    # This route is mainly for clearing the cookie on the browser
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200
