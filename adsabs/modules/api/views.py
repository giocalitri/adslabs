import sys
sys.path.append('..')

from flask import Blueprint, request, g, current_app as app
from flask.ext.pushrod import pushrod_view #@UnresolvedImport

from functools import wraps

import errors
import logging
from adsabs.core import solr
from adsabs.core.logevent import LogEvent
from .user import AdsApiUser
from .request import ApiSearchRequest, ApiRecordRequest
from config import config

#definition of the blueprint for the user part
api_blueprint = Blueprint('api', __name__,template_folder="templates", url_prefix='/api')
errors.init_error_handlers(api_blueprint)

def api_user_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        dev_key = request.args.get('dev_key', None)
        if not dev_key or len(dev_key) == 0:
            raise errors.ApiNotAuthenticatedError("no developer token provided")
        try:
            user = AdsApiUser.from_dev_key(dev_key)
        except Exception, e:
            import traceback
            exc_info = sys.exc_info()
            app.logger.error("User auth failure: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))
            user = None
        if not user:
            raise errors.ApiNotAuthenticatedError("unknown user")
        g.api_user = user
        return func(*args, **kwargs)
    return decorator

@api_blueprint.before_request
def get_api_version_header():
    g.api_version = request.headers.get('X-API-Version', config.API_CURRENT_VERSION)
        
@api_blueprint.after_request
def add_api_version_header(response):
    """
    Add default api version header if not already set
    """
    response.headers.setdefault('X-API-Version', g.api_version)
    return response

@api_blueprint.route('/settings/', methods=['GET'])
@api_user_required
@pushrod_view(xml_template="settings.xml", wrap='settings')
def settings():
    perms = g.api_user.get_dev_perms()
    allowed_fields = g.api_user.get_allowed_fields()
    perms.update({'allowed_fields': allowed_fields})
    return perms

@api_blueprint.route('/search/', methods=['GET'])
@api_user_required
@pushrod_view(xml_template="search.xml")
def search():
    search_req = ApiSearchRequest(request.args)
    if search_req.validate():
        resp = search_req.execute()
        return resp.search_response()
    raise errors.ApiInvalidRequest(search_req.input_errors())
        
        
@api_blueprint.route('/record/<path:identifier>', methods=['GET'])
@api_user_required
@pushrod_view(xml_template="record.xml", wrap='doc')
def record(identifier):
    record_req = ApiRecordRequest(identifier, request.args)
    if record_req.validate():
        resp = record_req.execute()
        if not resp.get_hits() > 0:
            raise errors.ApiRecordNotFound(identifier)
        return resp.record_response()
    raise errors.ApiInvalidRequest(record_req.errors())
        
#@api_blueprint.route('/record/<identifier>/<operator>', methods=['GET'])
#@api_user_required
#@pushrod_view(xml_template="record.xml")
#def record_operator(identifier, operator):
#    pass

#@api_blueprint.route('/mlt/', methods=['GET'])
#@api_user_required
#@pushrod_view(xml_template="mlt.xml")
#def mlt():
#    pass

@solr.signals.search_signal.connect
@solr.signals.error_signal.connect
def log_solr_event(sender, **kwargs):
    """
    extracts some data from the solr  for log/analytics purposes
    """
    
    if hasattr(g, 'api_user'):
        kwargs['dev_key'] = g.api_user.get_dev_key()
        event = LogEvent.new(request.url, **kwargs)
        logging.getLogger('api').info(event)