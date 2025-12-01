from app.utils import *
from sqlalchemy import desc
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import *

main = Blueprint("main", __name__)

#routing to index / home
@main.route("/")
def index():
    if Tournament.query.first() is None:
        return render_template_string(tpls["index_init_tpl"])
    else:
        t=Tournament.query.order_by(Tournament.date.desc()).first()
        tid=t.id
        entries = PrelimPlayer.query.filter_by(tournament_id=tid).all()
        ordered = sorted(entries, key=lambda e: (e.net_score, e.gross_score))
        
        topField=sorted(entries, key=lambda e: (e.net_score, e.gross_score))
        topField=topField[:len(topField) // 2 ]
        bottomField=sorted(entries, key=lambda e: (e.net_score, e.gross_score),reverse=True)
        bottomField=bottomField[:len(bottomField) // 2 ]
        rattlerPairings=zip(topField,bottomField)
        
        return render_template_string(tpls["index_tpl"],t=t,entries=entries,ordered=ordered,rattlerPairings=rattlerPairings)