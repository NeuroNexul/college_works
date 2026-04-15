from flask import Flask, url_for, redirect, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta
import redis
from celery import Celery, Task
from celery.schedules import crontab


# Additional utility imports
import os
from pathlib import Path
from dotenv import load_dotenv

# Load db
from db.db import db, create_migration
from routes.auth import create_admin_user

# Import the User model
from db.models import User

# Load all routes
from routes import auth, admin, user

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
            subdomain_matching=False)

app.config.from_object(__name__)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows the server to accept requests from different origins, which is useful for APIs.
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Initialize JWTManager for handling JSON Web Tokens
# This will be used for user authentication and authorization.
# It allows you to create, decode, and verify JWTs.
jwt = JWTManager(app)

# Add divmod to the Jinja2 environment
app.jinja_env.globals.update(divmod=divmod)

# Define basic configuration for the app
app.redis_client = redis.StrictRedis(
    host='localhost', port=6379, db=0, decode_responses=True)

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
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)  # Set to 12 hours


# Initialize the Bcrypt extension
# This will be used to hash passwords securely.
bcrypt = Bcrypt(app)
app.config["BCRYPT"] = bcrypt


# Mount SQLAlchemy to the Flask app
# This will allow the app to interact with a SQL database using the ORM.
# First create the 'db' directory if it does not exist.
#
# DATABASE_URL: The URL to the database. This can be a local SQLite database or a remote database like PostgreSQL.
#               Example: 'sqlite:///database.db'
db_path = os.path.join(os.path.abspath(os.getcwd()), './db')
os.makedirs(db_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
    os.path.join(os.path.abspath(os.getcwd()), './db/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
# And do the migrations
db.init_app(app)
create_migration(app)

# Create the tables in the database if they do not exist
with app.app_context():
    db.create_all()

    # Create an admin user if it doesn't exist
    create_admin_user()


# Import the routes blueprints
# This is a common pattern to keep the code organized.
# Each blueprint can have its own routes and views.
# The blueprints can be registered with the Flask application.
app.register_blueprint(auth.bp, url_prefix="/api/auth")
app.register_blueprint(admin.bp, url_prefix="/api/admin")
app.register_blueprint(user.bp, url_prefix="/api")


@app.route("/api", subdomain="<subdomain>")
@app.route("/api", subdomain="")
def index(subdomain=None):
    """
    The index route serves the main page of the application.
    It redirects to the appropriate subdomain if specified.
    """
    if subdomain:
        return redirect(url_for("index", _external=True, _scheme="http", subdomain=subdomain))
    return jsonify({"message": "Welcome to the Vehicle Parking App!"})


global celery_init_app
# Celery


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    # celery_app.Task = FlaskTask
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost:6379/1",
        result_backend="redis://localhost:6379/2",
        task_ignore_result=True,
        beat_schedule={
            # Name your scheduled task
            'send-daily-reminders': {
                'task': 'tasks.send_daily_reminders',  # Path to the task function
                # 'schedule': crontab(hour=0, minute=0),  # Run once every day at midnight
                'schedule': 30.0,  # Run once every 24 hours (in seconds)
            },
            'send-monthly-reports': {
                'task': 'tasks.send_monthly_reports',
                'schedule': crontab(day_of_month='1', hour=0, minute=0),
                # Run once every 60 seconds (for testing purposes, change to 30 days in production)
                # 'schedule': 60,
            },
        },
    ),
)

celery_app = celery_init_app(app)


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
