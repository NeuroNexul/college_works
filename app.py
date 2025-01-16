from flask import Flask, render_template, request, g
import sqlite3
from dotenv import load_dotenv
from pathlib import Path
import os
from controllers import db_controller
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
            template_folder="templates")

# Setup on demand database connection
# This is a common pattern to avoid creating a new connection for each request.
# The connection is created when the first request is received and is closed after the last request is processed.
# This way the connection is only open when it's needed.

# Define a function to get the database connection


def get_db():
    db: sqlite3.Connection = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("database.db")
    return db

# Define a function to close the database connection


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Setup the database
# This will open the context of the application outside the request.
with app.app_context():
    db_controller.create_tables(get_db().cursor())

# Import the routes blueprints
# This is a common pattern to keep the code organized.
# Each blueprint can have its own routes and views.
# The blueprints can be registered with the Flask application.
app.register_blueprint(auth.bp)


@app.route("/")
def hello_world():
    return render_template("index.html")

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
