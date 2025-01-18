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

## Database Observations

In this project we have used SQLite database. The database is stored in a file named `database.db`. The database has the following tables:

- `users` table: This table stores the user information.
- `subjects` table: This table stores the subjects for each course.
- `chapters` table: This table stores the chapters for each course.
- `quiz` table: This table stores the quiz questions for each chapter.
- `questions` table: This table stores the questions for each quiz.
- `scores` table: This table stores the scores for each user.

To view the database, you can use the [DB Browser for SQLite](https://sqlitebrowser.org/). Or, in the docker-compose file, you can use the `phpliteadmin` service to view the database. The `phpliteadmin` service is available at `http://localhost:8081/`. To start the `phpliteadmin` service, run the following command:

```bash
docker-compose up -d
```
