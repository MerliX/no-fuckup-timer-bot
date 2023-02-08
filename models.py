from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Failure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)


    def __repr__(self):
        return f'<Failure id={self.id} comment={self.comment}>'
