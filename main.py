from dbModels import *
from utils import *
from routes import *
from tpls import *
from jinja2 import DictLoader

app.jinja_loader = DictLoader({'base': tpls["base_tpl"]})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
