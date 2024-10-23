from app import db

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    wins = db.Column(db.Integer, nullable=False)
    losses = db.Column(db.Integer, nullable=False)

db.create_all()
