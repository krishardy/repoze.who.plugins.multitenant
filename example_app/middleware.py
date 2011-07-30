## middleware.py
from repoze.what.predicates import not_anonymous

class RepozeMiddleware(object):
    def __init__(self, app, signin_url):
        self._app = app
        self._signin_url = signin_url
    
    def __call__(self, environ, start_response):
        # need to check path_info to avoid infinite loop
        if not_anonymous().is_met(environ) or environ['PATH_INFO'] == self._signin_url:
            return self._app(environ, start_response)
        else:
            status = "301 Redirect"
            headers = [("Location", self._signin_url),]
            start_response(status, headers)
            return ["Not logged in",]
