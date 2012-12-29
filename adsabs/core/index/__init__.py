from flask import Blueprint, render_template, request, current_app
import os

from adsabs.modules.search.forms import QueryForm

#I define the blueprint
index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """
    Entry point of the web site
    """
    #I initialize the form
    search_form = QueryForm(request.values, csrf_enabled=False)
    #I look for the static html if there is some
    static_file_path = os.path.join(current_app.root_path, 'static', 'static_html', 'main_page_static_html.html')
    try:
        with open(static_file_path) as f: 
            static_content = f.read()
    except:
        static_content = ''
    return render_template('index/main_page.html', form=search_form, static_content=static_content)
