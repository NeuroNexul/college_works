<h1 align="middle">Modern Application Development I</h1>

<img
  src="https://lh7-rt.googleusercontent.com/docsz/AD_4nXfd9ouBAW-ZmgoB8ofs8V958xDE4v0RONwtWSiPg7Jb4hHeSfuDA1JNnaV52ISAvUHSZqgP1WG4tUAxbmq41_am9BAVa8i3Vp4CPwqEl8AMsWB816SKyNxrZMVFVBpdj0rxBOZVHQ?key=eTnvMdFybwOblM8547xjyiaQ"
  alt="Modern Application Development I"
  align="middle"
  style="border-radius: 10px"
/>

## Project Statement - Quiz Master - V1

It is a multi-user app (one requires an administrator and other users) that acts as an exam preparation site for multiple courses.

## Frameworks to be used

These are the mandatory frameworks on which the project has to be built.

- ![Flask](https://img.shields.io/badge/Flask-2.0.1-blue) Flask for application back-end
- ![Jinja2](https://img.shields.io/badge/Jinja2-3.0.1-blue) Jinja2 templating, HTML, CSS and Bootstraps for application front-end
- ![SQLite](https://img.shields.io/badge/SQLite-3.0.1-blue) SQLite for database (No other database is permitted)

**Note:** All demos should be possible on your local machine.

## Setup Instructions

### Create a new [Python virtual Environment](https://docs.python.org/3/library/venv.html), activate and install the required packages:

```bash
# Create a new Python virtual environment
py -3 -m venv .venv

# Activate the virtual environment
.venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt
```

### Setup the Database

Create the database and populate it with some initial data:

```bash
# Create the database
python create_db.py
```

## Running the Application

Run the application:

```bash
python app.py
```

The application will be available at `http://localhost:5000/`.
