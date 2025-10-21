from app.utils import *
from sqlalchemy.exc import OperationalError

main = Blueprint("main", __name__)

#routing to index / home
@main.route("/")
def index():
    return render_template_string(tpls["index_tpl"])