from flask import Flask, url_for, redirect, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt


# Additional utility imports
import os
from pathlib import Path
from dotenv import load_dotenv

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
CORS(app, resources={r"/*": {"origins": "*"}})

# Add divmod to the Jinja2 environment
app.jinja_env.globals.update(divmod=divmod)

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


@app.route("/", subdomain="<subdomain>")
@app.route("/", subdomain="")
def index(subdomain=None):
    """
    The index route serves the main page of the application.
    It redirects to the appropriate subdomain if specified.
    """
    if subdomain:
        return redirect(url_for("index", _external=True, _scheme="http", subdomain=subdomain))
    return jsonify({"message": "Welcome to the Vehicle Parking App!"})


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
