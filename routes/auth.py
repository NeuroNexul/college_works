from flask import Blueprint, render_template, request, redirect, url_for, session, g, current_app
from models import db, User
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get the form data
        username = request.form["username"]
        password = request.form["password"]
        full_name = request.form["full_name"]
        qualification = request.form["qualification"]
        dob = datetime.strptime(request.form["dob"], "%Y-%m-%d")

        # Hash the password
        # hash_password = Bcrypt().generate_password_hash(password).decode("utf-8")
        bcrypt = current_app.config["BCRYPT"]
        hash_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Check for existing user
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return render_template("auth/register.html", errors=["An user with the same username/email already exists"])

        # Create new User
        new_user = User(username=username, password=hash_password,
                        full_name=full_name, qualification=qualification, dob=dob)

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log the user in
        login_user(new_user)

        # Redirect to the home page
        return redirect(url_for("hello_world"))
    else:
        if current_user.is_authenticated:
            return redirect(url_for("hello_world"))
        else:
            return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get the form data
        username = request.form["username"]
        password = request.form["password"]

        # Check for existing user
        user = User.query.filter_by(username=username).first()

        # If the user exists
        if user is not None:
            # Check the password
            bcrypt = current_app.config["BCRYPT"]
            if bcrypt.check_password_hash(user.password, password):
                # Log the user in
                login_user(user)

                # Redirect to the home page
                return redirect(url_for("hello_world"))
            else:
                return render_template("auth/login.html", errors=["Invalid password"])
        else:
            return render_template("auth/login.html", errors=["Invalid username"])

    else:
        if current_user.is_authenticated:
            return redirect(url_for("hello_world"))
        else:
            return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    # Log the user out
    logout_user()

    # Redirect to the login page
    return redirect(url_for("auth.login"))
