from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sports.db'
db = SQLAlchemy(app)

API_KEY = 'fc436e74c9024ccaba8e2a245d15efc6'
BASE_URL = 'https://sportsdata.io/developers/api-documentation/soccer#period-game-odds-line-movement'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    wins = db.Column(db.Integer, nullable=False)
    losses = db.Column(db.Integer, nullable=False)

with app.app_context():
    teams = Team.query.all()
    for team in teams:
        print(f"Team: {team.name}, Wins: {team.wins}, Losses: {team.losses}")

@app.route('/')
def index():
    teams = Team.query.all()
    return render_template('index.html', teams=teams)

@app.route('/update')
def update():
    response = requests.get(BASE_URL, headers={'Ocp-Apim-Subscription-Key': API_KEY})
    if response.status_code != 200:
        return f"API Hatası: {response.status_code}, Detay: {response.text}"
    
    if not response.text.strip():
        return "API'den boş yanıt alındı"
    
    try:
        teams_data = response.json()
    except ValueError as e:
        return f"JSON Hatası: {e}"

    print(teams_data)  # API yanıtını kontrol et
    for team in teams_data:
        print(f"Ekleme: {team['Name']}, Wins: {team.get('Wins', 0)}, Losses: {team.get('Losses', 0)}")
        existing_team = Team.query.filter_by(name=team['Name']).first()
        if existing_team:
            existing_team.wins = team.get('Wins', existing_team.wins)
            existing_team.losses = team.get('Losses', existing_team.losses)
        else:
            new_team = Team(name=team['Name'], wins=team.get('Wins', 0), losses=team.get('Losses', 0))
            db.session.add(new_team)
    db.session.commit()
    return redirect('/')


@app.route('/results')
def results():
    teams = Team.query.order_by(Team.wins.desc()).all()
    return render_template('results.html', teams=teams)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        team1 = request.form['team1']
        team2 = request.form['team2']
        team1_wins = Team.query.filter_by(name=team1).first().wins
        team2_wins = Team.query.filter_by(name=team2).first().wins
        prediction = team1 if team1_wins > team2_wins else team2
        return render_template('prediction.html', prediction=prediction)
    return render_template('predict.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
