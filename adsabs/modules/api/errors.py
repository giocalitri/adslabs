'''
Created on Nov 2, 2012

@author: jluker
'''

from flask.ext.pushrod import pushrod_view #@UnresolvedImport

class ApiNotAuthenticatedError(Exception):
    pass

class ApiInvalidRequest(Exception):
    pass

class ApiPermissionError(Exception):
    pass

class ApiRecordNotFound(Exception):
    pass

def init_error_handlers(app):
    @app.errorhandler(ApiNotAuthenticatedError)
    @pushrod_view(xml_template="error.xml")
    def not_authenticated(error):
        msg = "API authentication failed: %s" % error.message
        return {'error': msg},401,None
    
    @app.errorhandler(ApiInvalidRequest)
    @pushrod_view(xml_template="error.xml")
    def invalid_request(error):
        msg = "API request invalid: %s" % error.message
        return {'error': msg},401,None
    
    @app.errorhandler(ApiPermissionError)
    @pushrod_view(xml_template="error.xml")
    def permission_error(error):
        msg = "Permission error: %s " % error.message
        return {'error': msg},401,None

    @app.errorhandler(ApiRecordNotFound)
    @pushrod_view(xml_template="error.xml")
    def record_not_found(error):
        msg = "No record found with identifier %s" % error.message
        return {'error': msg},404,None