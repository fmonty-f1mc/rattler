from app.tpls import *
from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash, Blueprint
from datetime import datetime
from jinja2 import DictLoader
import io
import csv
from math import ceil, floor

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect,update,delete

    
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
    