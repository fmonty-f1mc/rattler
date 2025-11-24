from app.utils import *
from app.models import *
from app import db, bcrypt

tournaments=Blueprint("tournaments",__name__)

@tournaments.route('/tournaments')
def tournament_view():
    return render_template_string(tpls["tournaments_tpl"], retTable=Tournament.query.all())

@tournaments.route('/tournaments/create', methods=['GET', 'POST'])
def create_tournament():
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        course_rating = request.form.get('course_rating')
        yardage = request.form.get('yardage')
        t = Tournament(course_name=course_name, date=date,course_rating=course_rating,yardage=yardage)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('tournaments.tournament_view'))

    return render_template_string(tpls['tournaments_create_tpl'])

@tournaments.route('/tournaments/<int:tid>', methods=['GET', 'POST'])
def view_tournament(tid):
    t = Tournament.query.get_or_404(tid)
    all_players = Player.query.all()
    entries = PrelimPlayer.query.filter_by(tournament_id=tid).all()
    ordered = sorted(entries, key=lambda e: (e.net_score, e.gross_score))
    
    topField=sorted(entries, key=lambda e: (e.net_score, e.gross_score))
    topField=topField[:len(topField) // 2 ]
    bottomField=sorted(entries, key=lambda e: (e.net_score, e.gross_score),reverse=True)
    bottomField=bottomField[:len(bottomField) // 2 ]
    rattlerPairings=zip(topField,bottomField)
    
    if request.method == 'POST':
        pid = int(request.form.get('player_id'))
        pName= Player.query.get_or_404(pid).name
        if request.form.get('action') in ('Add Player with Player Handicap','Add Player with Tournament Handicap'):
            
            if PrelimPlayer.query.filter_by(tournament_id=tid, player_id=pid).first():
                flash(f'{pName} already added')
                
            elif request.form.get('action') == 'Add Player with Player Handicap':
                p=PrelimPlayer(tournament_id=tid, player_id=pid)
                db.session.add(p)
                p.tournament_handicap=Player.query.get_or_404(pid).handicap
                db.session.commit()
                flash(f'{pName} added with Player Handicap')
                return redirect(url_for('tournaments.view_tournament', tid=tid))
            
            elif request.form.get('action') == 'Add Player with Tournament Handicap':
                p=PrelimPlayer(tournament_id=tid, player_id=pid)
                db.session.add(p)
                p.tournament_handicap=request.form.get('tournament_handicap')
                db.session.commit()
                flash(f'{pName} added with Tournament Handicap')
                return redirect(url_for('tournaments.view_tournament', tid=tid))
        if request.form.get('action') == 'Remove Player':
            if PrelimPlayer.query.filter_by(tournament_id=tid, player_id=pid).first() is not None:
                e = PrelimPlayer.query.filter_by(tournament_id=tid, player_id=pid).first()
                db.session.delete(e)
                db.session.commit()
                flash(f'{pName} Removed from tournament')
                return redirect(url_for('tournaments.view_tournament', tid=tid))
            else:
                flash('Player is not Added to Tournament')
                return redirect(url_for('tournaments.view_tournament', tid=tid))
        else:
            flash("Error on the program")
            
    #if request.method == 'POST':
    #    pid = int(request.form.get('player_id'))
    #    if PrelimPlayer.query.filter_by(tournament_id=tid, player_id=pid).first():
    #        flash('Player already added')
    #    else:
    #        db.session.add(PrelimPlayer(tournament_id=tid, player_id=pid))
    #        db.session.commit()
    #        flash('Player added')
    #    return redirect(url_for('tournaments.view_tournament', tid=tid))
    
    return render_template_string(tpls['prelimPlayer_tpl'], t=t, all_players=all_players, entries=entries,ordered=ordered,rattlerPairings=rattlerPairings)

@tournaments.route('/tournaments/<int:tid>/edit', methods=['GET', 'POST'])
def edit_tournament(tid):
    t=Tournament.query.get_or_404(tid)
    if request.method == 'POST':

        t.date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        t.course_name=request.form.get('course_name')
        t.course_rating=request.form.get('course_rating')
        t.yardage=request.form.get('yardage')
        
        db.session.commit()
        return redirect(url_for('tournaments.tournament_view'))
    return render_template_string(tpls['tournament_edit_tpl'], t=t)

@tournaments.route('/tournaments/<int:tid>/leaderboard')
def leaderboard(tid):
    t = Tournament.query.get_or_404(tid)
    entries = PrelimPlayer.query.filter_by(tournament_id=tid).all()
    ordered = sorted(entries, key=lambda e: (e.net_score, e.gross_score))
    return render_template_string(tpls['tournament_leaderboard_tpl'], t=t, ordered=ordered)

@tournaments.route('/tournaments/<int:tid>/score/<int:eid>', methods=['GET','POST'])
def score_entry(tid, eid):
    e = PrelimPlayer.query.get_or_404(eid)
    tid=tid
    gross_score=e.gross_score
    if request.method == 'POST':
        score = int(request.form.get('post_score'))
        e.update_scores(score)
        db.session.commit()
        flash('Scores saved')
        return redirect(url_for('tournaments.view_tournament', tid=tid))
    return render_template_string(tpls['score_entry_tpl'], e=e, gross_score=gross_score)

@tournaments.route('/tournaments/<int:tid>/remove/<int:eid>', methods=['GET','POST'])
def prelim_player_remove(tid, eid):
    e = PrelimPlayer.query.get_or_404(eid)
    p = Player.query.where(Player.id == e.player_id)
    if request.method == 'POST':
        db.session.delete(e)
        db.session.commit()
        flash('Player Removed from Tournament')
        return redirect(url_for('tournaments.view_tournament', tid=tid))
    return render_template_string(tpls['prelim_player_remove'], e=e,p=p)

@tournaments.route('/tournaments/<int:tid>/add/<int:pid>', methods=['GET','POST'])
def prelim_player_add(tid, pid):
    if request.method == 'POST':
        if PrelimPlayer.query.filter_by(tournament_id=tid, player_id=pid).first():
            flash('Player already added')
        else:
            db.session.add(PrelimPlayer(tournament_id=tid, player_id=pid))
            db.session.commit()
            flash('Player added')
        return redirect(url_for('tournaments.view_tournament', tid=tid))