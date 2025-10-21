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