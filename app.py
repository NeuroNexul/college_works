from flask import Flask, render_template, request, g, session
import sqlite3
from flask_bootstrap import Bootstrap5
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from pathlib import Path
import os
from models import db, create_migration, User
from flask_login import LoginManager, current_user

from routes import auth


# Load environment variables from a .env file
# This is useful to keep sensitive data like API keys out of the codebase.
# The .env file should be in the root of the project.
# Example: API_KEY=1234567890
dotenv_path = Path(".") / ".env"
load_dotenv(dotenv_path=dotenv_path)


# Create a new Flask instance
# __name__ is a special Python variable that gets as value the string "__main__"
# when you’re executing the script.
#
# static_folder: The folder with static files that will be served at /static URL.
# template_folder: The folder with HTML templates that will be used to render pages using Jinja2 template engine.

app = Flask(__name__,
            static_folder="static",
            template_folder="templates",
            subdomain_matching=True)

# Mount SQLAlchemy to the Flask app
# This will allow the app to interact with a SQL database using the ORM.
#
# DATABASE_URL: The URL to the database. This can be a local SQLite database or a remote database like PostgreSQL.
#               Example: 'sqlite:///database.db'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
    os.path.join(os.path.abspath(os.getcwd()), './db/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Do the migrations
create_migration(app)

# Create the tables in the database if they do not exist
with app.app_context():
    db.create_all()

# Initialize the app with Bootstrap5
bootstrap = Bootstrap5(app)


# Define basic configuration for the app

# Enable subdomain matching
# This allows the app to match subdomains in the URL routes and serve different content based on the subdomain.
# For example, you could have different content for 'app.example.com' and 'api.example.com'.
#
# SERVER_NAME: The name of the server. This is used to generate URLs outside of the request context.
#              Example: 'example.com:5000'

app.config["SERVER_NAME"] = os.getenv("SERVER_NAME")

# Set the default subdomain. Flask will serve the root content to this subdomain.
# To serve content to the root domain, set this to an empty string.

app.url_map.default_subdomain = ""

# Set the secret key to enable sessions
# The secret key is used to secure the session data.
# It should be a random string with high entropy.

app.secret_key = os.getenv("SECRET_KEY")

# Initialize the Bcrypt extension
# This will be used to hash passwords securely.
bcrypt = Bcrypt(app)
app.config["BCRYPT"] = bcrypt

# Initialize the LoginManager extension
# This will be used to manage user authentication.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# Define the function that will be called to load a user
# This function should return the user object based on the user ID.
# The user ID is stored in the session cookie and is used to load the user object.
# The user object should implement the UserMixin class from Flask-Login.


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Import the routes blueprints
# This is a common pattern to keep the code organized.
# Each blueprint can have its own routes and views.
# The blueprints can be registered with the Flask application.


app.register_blueprint(auth.bp)


@app.route("/")
def hello_world():
    # return render_template("index.html")
    if current_user.is_authenticated:
        return str(current_user.username)
    else:
        return "Hello, World!"


# Start the server with the 'run()' method, if the script is executed directly.
# This is the main entry point for the application.
#
# host: The hostname to listen on. Defaults to '0.0.0.0'
# port: The port of the webserver. Defaults to 5000
# debug: If set to True, the server will automatically reload after code changes.

if __name__ == "__main__":
    try:
        # Retrieve environment variables
        server_host = os.getenv("SERVER_HOST")
        server_port = os.getenv("SERVER_PORT")
        server_debug = os.getenv("SERVER_DEBUG")

        # Start the server
        app.run(host=server_host, port=server_port, debug=bool(server_debug))

    except Exception as e:
        print(f"An error occurred: {e}")
