from app import app


flask_app = app
celery_app = flask_app.extensions["celery"]
