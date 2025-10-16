from dbModels import *
from tpls import *

def init_db():
    db.create_all()
    
def get_html(file_location):
    with open(f"{file_location}.html", 'r', encoding='utf-8') as file:
        # Read the entire content of the file into a string
        return file.read()

def emptyTablePageHandler(dbTable,redirectFunc,viewTpl):
    
    inspector = inspect(db.engine)
    table_exists = inspector.has_table(dbTable)
    
    if table_exists is False:
        return redirect(url_for(redirectFunc))
    elif globals()[dbTable].query.count() == 0:
        return redirect(url_for(redirectFunc))
    else:
        return render_template_string(tpls[viewTpl], retTable=globals()[dbTable].query.all())
    
    
