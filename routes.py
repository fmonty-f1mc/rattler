from dbModels import *
from utils import *
from tpls import *

#routing to index / home
@app.route('/')
def index():
    return render_template_string(tpls["index_tpl"])

@app.route('/tournaments')
def tournaments():
    return emptyTablePageHandler("tournament","create_tournament","tournaments_tpl")

@app.route('/tournaments/create', methods=['GET', 'POST'])
def create_tournament():
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        course_rating = request.form.get('course_rating')
        yardage = request.form.get('yardage')
        t = tournament(course_name=course_name, date=date,course_rating=course_rating,yardage=yardage)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('tournaments'))

    return render_template_string(tpls['tournaments_create_tpl'])


@app.route('/players')
def players():
    return emptyTablePageHandler("player","create_player","players_tpl")

@app.route('/players/create', methods=['GET','POST'])
def create_player():
    if request.method == 'POST':
        p = player(name=request.form.get('name'), 
                   email=request.form.get('email'), 
                   handicap=float(request.form.get('handicap') or 0)
                   )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('players'))
    return render_template_string(tpls["players_create_tpl"])

@app.route('/divisions')
def divisions():
    return emptyTablePageHandler("division","create_division","divisions_tpl")

@app.route('/divisions/create', methods=['GET','POST'])
def create_division():
    if request.method == 'POST':
        d = division(name=request.form.get('name'))
        db.session.add(d)
        db.session.commit()
        return redirect(url_for('divisions'))
    return render_template_string(tpls["divisions_create_tpl"])







