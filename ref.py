"""
Rattler Tournament - Single-file Flask app

Features:
- Create tournaments (name, date, number of holes, flight size)
- Add/edit players (name, email, handicap)
- Assign players to tournaments
- Generate pairings (groups of up to 4) balancing by handicap
- Record scores per player and hole (simple entry)
- View leaderboard and pairings
- Export players/pairings as CSV

Run instructions:
1) Create a virtualenv and install requirements:
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install flask sqlalchemy flask_sqlalchemy pandas

2) Run the app:
   FLASK_APP=golf_tournament_planner.py flask run --host=0.0.0.0 --port=5000

This file stores an SQLite database 'tournaments.db' in the same folder.

Note: This is a lightweight starter app. If you want user auth, PDF exports, tee-time scheduling, or
mobile-friendly UI, I can add them.
"""
"""
Rattler Tournament with Leaderboard Link

Added features:
- Score entry per hole for each player in a tournament
- Handicap stroke allocation (simple: handicap ÷ total holes, rounded)
- Net score calculation = gross score − allocated strokes
- Leaderboard view linked from tournament page
"""
from datetime import datetime
import io
import csv
from math import ceil, floor

from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "dev-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tournaments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
### Database Models  ###
# ----------------------

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    prelimround=db.Column(db.Integer, db.ForeignKey('prelimround.id'))
    rattlerround=db.Column(db.Integer,db.ForeignKey('rattlerround.id'))

class PrelimRound(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    #holes = db.Column(db.Integer,default=18)
    players = db.relationship('PrelimPlayer', back_populates='prelimround', cascade='all, delete-orphan')
    
class RattlerRound(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    #holes = db.Column(db.Integer,default=9)
    pairings = db.relationship('RattlerPairing',back_populates='ratterround',cascade='all, delete-orphan')

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200))
    handicap = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    division = db.Column(db.Integer,db.ForeignKey('division.id'))
    entries = db.relationship('PrelimPlayer', back_populates='player', cascade='all, delete-orphan')

class PrelimPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    gross_score = db.Column(db.Integer, default=0)
    net_score = db.Column(db.Integer, default=0)
    #hole_scores = db.Column(db.String(400), default='')

    tournament = db.relationship('PrelimRound', back_populates='players')
    player = db.relationship('Player', back_populates='entries')
    db.Column(db.Integer, db.ForeignKey('prelimround.id'))

    #def scores_list(self):
    #    return [int(x) for x in self.hole_scores.split(',') if x.strip().isdigit()]

    def update_scores(self, score):
        #self.hole_scores = ','.join(str(s) for s in scores)
        self.gross_score = sum(score)
        strokes_allocated = floor(self.player.handicap)
        self.net_score = self.gross_score - strokes_allocated

class RattlerPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    pairing = db.relationship('RattlerPairing',back_populates='rattlerplayer')
    
    
class RattlerPairing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.Integer,nullable=False)
    player1 = db.Column(db.Integer, db.ForeignKey('rattlerplayer.id'))
    player2 = db.Column(db.Integer, db.ForeignKey('rattlerplayer.id'))
    
class Division(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    players = db.relationship('Player', back_populates='division', cascade='all, delete-orphan')
    

# ----------------------
# Utilities
# ----------------------
def init_db():
    db.create_all()

def balance_pairings(players, group_size=4):
    if not players:
        return []
    sorted_list = sorted(players, key=lambda tp: tp.player.handicap, reverse=True)
    num_groups = ceil(len(sorted_list) / group_size)
    groups = [[] for _ in range(num_groups)]
    index, direction = 0, 1
    for tp in sorted_list:
        groups[index].append(tp)
        index += direction
        if index >= num_groups:
            index = num_groups - 1
            direction = -1
        elif index < 0:
            index = 0
            direction = 1
    return groups

# ----------------------
# Templates
# ----------------------
base_tpl = """
<!doctype html>
<title>Rattler Tournament</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
<header>
  <h1>Rattler Tournament</h1>
  <nav>
    <a href="{{ url_for('index') }}">Home</a> |
    <a href="{{ url_for('tournaments') }}">Tournaments</a> |
    <a href="{{ url_for('players') }}">Players</a>
  </nav>
</header>
<main>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <ul>
      {% for m in messages %}
        <li>{{ m }}</li>
      {% endfor %}
      </ul>
    {% endif %}
  {% endwith %}
  {% block content %}{% endblock %}
</main>
"""

index_tpl = """
{% extends 'base' %}
{% block content %}
  <h2>Welcome</h2>
  <p>Create a tournament, add players, enter scores, and view leaderboard.</p>
{% endblock %}
"""

@app.route('/')
def index():
    return render_template_string(index_tpl)

@app.route('/tournaments')
def tournaments():
    tournaments = Tournament.query.order_by(Tournament.date.desc()).all()
    tpl = """
    {% extends 'base' %}
    {% block content %}
      <h2>Tournaments</h2>
      <a href="{{ url_for('create_tournament') }}">+ Create new tournament</a>
      <ul>
      {% for t in tournaments %}
        <li><strong>{{ t.name }}</strong> — {{ t.date }} [<a href="{{ url_for('view_tournament', tid=t.id) }}">view</a>]</li>
      {% endfor %}
      </ul>
    {% endblock %}
    """
    return render_template_string(tpl, tournaments=tournaments)

@app.route('/tournaments/create', methods=['GET', 'POST'])
def create_tournament():
    if request.method == 'POST':
        name = request.form.get('name')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        #holes = int(request.form.get('holes'))
        t = Tournament(name=name, date=date)
        db.session.add(t)
        #db.session.add(PrelimRound())
        #db.session.add(RattlerRound())
        db.session.commit()
        return redirect(url_for('tournaments'))
    tpl = """
    {% extends 'base' %}
    {% block content %}
    <h2>Create Tournament</h2>
    <form method="post">
      <input name="name" placeholder="Name" required><br>
      <input name="date" placeholder="YYYY-MM-DD" required><br>
      <button type="submit">Create</button>
    </form>
    {% endblock %}
    """
    return render_template_string(tpl)

@app.route('/tournaments/<int:tid>', methods=['GET', 'POST'])
def view_tournament(tid):
    t = Tournament.query.get_or_404(tid)
    all_players = Player.query.all()
    entries = PrelimPlayer.query.filter_by(tournament_id=tid).all()
    if request.method == 'POST':
        pid = int(request.form.get('player_id'))
        if PrelimPlayer.query.filter_by(tournament_id=tid, player_id=pid).first():
            flash('Player already added')
        else:
            db.session.add(PrelimPlayer(tournament_id=tid, player_id=pid))
            db.session.commit()
            flash('Player added')
        return redirect(url_for('view_tournament', tid=tid))
    tpl = """
    {% extends 'base' %}
    {% block content %}
    <h2>{{ t.name }}</h2>
    <!-- <p>Holes: {{ t.holes }}</p> -->
    <form method="post">
      <select name="player_id">
      {% for p in all_players %}
        <option value="{{ p.id }}">{{ p.name }} (hcp {{ p.handicap }})</option>
      {% endfor %}
      </select>
      <button type="submit">Add Player</button>
    </form>
    <ul>
    {% for e in entries %}
      <li>{{ e.player.name }} — <a href="{{ url_for('score_entry', tid=t.id, eid=e.id) }}">Enter Scores</a></li>
    {% endfor %}
    </ul>
    <p><a href="{{ url_for('leaderboard', tid=t.id) }}">View Leaderboard</a></p>
    {% endblock %}
    """
    return render_template_string(tpl, t=t, all_players=all_players, entries=entries)

@app.route('/tournaments/<int:tid>/score/<int:eid>', methods=['GET','POST'])
def score_entry(tid, eid):
    e = PrelimPlayer.query.get_or_404(eid)
    t = e.tournament
    #holes = t.holes
    #scores = e.scores_list() or [0]*holes
    gross_score=e.gross_score
    if request.method == 'POST':
        #scores = [int(request.form.get(f'h{i}', 0)) for i in range(1, holes+1)]
        e.update_scores(gross_score)
        db.session.commit()
        flash('Scores saved')
        return redirect(url_for('view_tournament', tid=tid))
    tpl = """
    {% extends 'base' %}
    {% block content %}
    <h2>Score Entry — {{ e.player.name }}</h2>
    <form method="post">
      <tr>
        <td><input name="Gross Score" value="{{ gross_score }}" size"3"></td>
      <!-- <table>
        <tr>
          {% for i in range(1, holes+1) %}
          <th>{{ i }}</th>
          {% endfor %}
        </tr>
        <tr>
          {% for i in range(holes) %}
          <td><input name="h{{ i+1 }}" value="{{ scores[i] }}" size="2"></td>
          {% endfor %}
        </tr>
      </table> -->
       </tr>
      <button type="submit">Save</button>
    </form>
    {% endblock %}
    """
    return render_template_string(tpl, e=e, gross_score=gross_score)

@app.route('/tournaments/<int:tid>/leaderboard')
def leaderboard(tid):
    t = Tournament.query.get_or_404(tid)
    entries = TournamentPlayer.query.filter_by(tournament_id=tid).all()
    ordered = sorted(entries, key=lambda e: (e.net_score, e.gross_score))
    tpl = """
    {% extends 'base' %}
    {% block content %}
    <h2>Leaderboard — {{ t.name }}</h2>
    <ol>
    {% for e in ordered %}
      <li>{{ e.player.name }} — Gross: {{ e.gross_score }} | Net: {{ e.net_score }}</li>
    {% endfor %}
    </ol>
    <p><a href="{{ url_for('view_tournament', tid=t.id) }}">Back to Tournament</a></p>
    {% endblock %}
    """
    return render_template_string(tpl, t=t, ordered=ordered)

@app.route('/players')
def players():
    players = Player.query.all()
    tpl = """
    {% extends 'base' %}
    {% block content %}
    <h2>Players</h2>
    <a href="{{ url_for('create_player') }}">Add Player</a>
    <ul>
    {% for p in players %}
      <li>{{ p.name }} (hcp {{ p.handicap }})</li>
    {% endfor %}
    </ul>
    {% endblock %}
    """
    return render_template_string(tpl, players=players)

@app.route('/players/create', methods=['GET','POST'])
def create_player():
    if request.method == 'POST':
        p = Player(name=request.form.get('name'), email=request.form.get('email'), handicap=float(request.form.get('handicap') or 0))
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('players'))
    tpl = """
    {% extends 'base' %}
    {% block content %}
    <h2>Add Player</h2>
    <form method="post">
      <input name="name" placeholder="Name" required><br>
      <input name="email" placeholder="Email"><br>
      <input name="handicap" value="0"><br>
      <button type="submit">Add</button>
    </form>
    {% endblock %}
    """
    return render_template_string(tpl)

from jinja2 import DictLoader
app.jinja_loader = DictLoader({'base': base_tpl})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
