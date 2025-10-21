from app.utils import *
from app import db, bcrypt
from app.models import Player

players= Blueprint("players",__name__)

@players.route('/players')
def player_view():
    return render_template_string(tpls["players_tpl"], retTable=Player.query.all())

@players.route('/players/create', methods=['GET','POST'])
def create_player():
    if request.method == 'POST':
        p = Player(name=request.form.get('name'), 
                   email=request.form.get('email'), 
                   handicap=float(request.form.get('handicap') or 0)
                   )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('players.player_view'))
    return render_template_string(tpls["players_create_tpl"])