from app.utils import *
from app import db, bcrypt
from app.models import Player,Division


players= Blueprint("players",__name__)

@players.route('/players')
def player_view():
    return render_template_string(tpls["players_tpl"], retTable=Player.query.all())

@players.route('/players/create', methods=['GET','POST'])
def create_player():
    all_divisions=Division.query.all()
    if request.method == 'POST':
        p = Player(name=request.form.get('name'), 
                   email=request.form.get('email'), 
                   handicap=float(request.form.get('handicap') or 0),
                   division_id=request.form.get('division') ,
                   )
        db.session.add(p)
        db.session.commit()
        
        return redirect(url_for('players.player_profile',pid=p.id))
    return render_template_string(tpls["players_create_tpl"],all_divisions=all_divisions)

@players.route('/players/<int:pid>', methods=['GET', 'POST'])
def player_profile(pid):
    p = Player.query.get_or_404(pid)
    return render_template_string(tpls['player_profile_tpl'], p=p)

@players.route('/players/<int:pid>/edit', methods=['GET', 'POST'])
def edit_player(pid):
    p=Player.query.get_or_404(pid)
    all_divisions=Division.query.all()
    if request.method == 'POST':

        p.name=request.form.get('name')
        p.email=request.form.get('email')
        p.handicap=float(request.form.get('handicap'))
        p.division_id=request.form.get('division')
        
        db.session.commit()
        return redirect(url_for('players.player_view'))
    return render_template_string(tpls['player_profile_edit_tpl'], p=p,all_divisions=all_divisions)

@players.route('/players/<int:pid>/remove/', methods=['GET','POST'])
def delete_player(pid):
    p = Player.query.get_or_404(pid)
    if request.method == 'POST':
        db.session.delete(p)
        db.session.commit()
        flash('Player Removed from Db')
        return redirect(url_for('player_view'))
    return render_template_string(tpls['player_delete_tpl'], p=p)