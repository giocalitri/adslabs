'''
Created on Nov 12, 2012

@author: jluker
'''

import fixtures
from simplejson import dumps

def user_creator():
    def func(username, developer=False, dev_perms=None):
        from adsabs.extensions import mongodb
        user_collection = mongodb.session.db.ads_users #@UndefinedVariable
        user_data = {
            "username": username + "_name",
            "myads_id": username + "_myads_id",
            "cookie_id": username + "_cookie_id",
        }
        
        if developer:
            user_data['developer_key'] = username + "_dev_key"
            
        if dev_perms:
            user_data['developer_perms'] = dev_perms
            
        user_collection.insert(user_data)
    return func
    
class SolrRawQueryFixture(fixtures.MonkeyPatch):
    
    DEFAULT_RESPONSE = {
        'responseHeader': {
            'params': {
                'q': 'abc',
            }
        },
        'response': {
            'numFound': 1,
            'docs': [{
                      'bibcode': 'xyz'
                    }],
            'facets': [ ('bar', 1) ]
        }
    }
    
    def __init__(self, data=None, **kwargs):
        if data is None:
            data = self.DEFAULT_RESPONSE
        self.resp_data = data
        
        def raw_query(*args_, **kwargs_):
            return dumps(self.resp_data)
        
        fixtures.MonkeyPatch.__init__(self, 'solr.SolrConnection.raw_query', raw_query)
        
    def set_data(self, data):
        self.resp_data = data
        