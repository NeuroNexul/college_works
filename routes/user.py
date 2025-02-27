from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import current_user
from datetime import datetime
from models import Quiz, Question

bp = Blueprint("user", __name__)


@bp.route("/dashboard")
def dashboard():
    # Fetch quizzes from the database along with the number of questions and the date
    quizzes = Quiz.query.all()
    print(quizzes)
    
    # quizzes = [
    #     {
    #         'id': 1,
    #         'num_questions': 5,
    #         'date': datetime(2025, 3, 10),
    #         'duration': 10,  # Duration in minutes
    #     },
    #     {
    #         'id': 2,
    #         'num_questions': 10,
    #         'date': datetime(2025, 3, 15),
    #         'duration': 10,
    #     },
    #     {
    #         'id': 3,
    #         'num_questions': 15,
    #         'date': datetime(2025, 3, 20),
    #         'duration': 30,
    #     },
    # ]

    if current_user.is_authenticated:
        return render_template("user/dashboard.html", user=current_user, quizzes=quizzes)
    else:
        return redirect(url_for("auth.login"))
