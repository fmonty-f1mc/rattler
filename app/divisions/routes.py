from app.utils import *
from app.models import Division
from app import db, bcrypt

divisions=Blueprint("divisions",__name__)

@divisions.route('/divisions')
def division_view():
    return render_template_string(tpls["divisions_tpl"], retTable=Division.query.all())

@divisions.route('/divisions/create', methods=['GET','POST'])
def create_division():
    if request.method == 'POST':
        d = Division(name=request.form.get('name'))
        db.session.add(d)
        db.session.commit()
        return redirect(url_for('divisions.division_view'))
    return render_template_string(tpls["divisions_create_tpl"])