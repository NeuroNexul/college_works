from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin

db = SQLAlchemy()


def create_migration(app):
    migrate = Migrate(app, db)

    return migrate


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    qualification = db.Column(db.String, nullable=False)
    dob = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}')>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Subject(name='{self.name}')>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey(
        'subjects.id'), nullable=False)

    def __repr__(self):
        return f"<Chapter(name='{self.name}')>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Quiz(db.Model):
    __tablename__ = 'quiz'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey(
        'chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.String, nullable=False)
    remarks = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Quiz(date_of_quiz='{self.date_of_quiz}')>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.String, nullable=False)
    correct_option = db.Column(db.String, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String, nullable=False)
    option4 = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Question(question_statement='{self.question_statement}')>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Score(score='{self.score}')>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
