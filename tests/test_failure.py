import os
import pytest

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Failure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(255), nullable=False)

db.create_all()

def handle_failure(comment):
    failure = Failure(comment=comment)
    db.session.add(failure)
    db.session.commit()

def test_handle_failure():
    comment = "Test failure comment"
    handle_failure(comment)

    failure = Failure.query.first()
    assert failure.comment == comment
