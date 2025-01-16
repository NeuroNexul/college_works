from flask import Blueprint, render_template, request

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get the form data
        username = request.form["username"]
        password = request.form["password"]

        # Check if the username and password are correct
        if username == "admin@mail.com" and password == "admin":
            return "Logged in successfully"
        else:
            return render_template("auth/login.html", errors=["Invalid username or password"])
        
    else:
        return render_template("auth/login.html")
