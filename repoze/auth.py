'''
Created on Apr 8, 2011

@author: kris
'''
import logging
from leanlog_server.model import Session, User, AclGroup, AclPermission, Company
from repoze.who.interfaces import IIdentifier, IChallenger
#from repose.who.plugins.auth_tkt import make_plugin
#from repoze.who.plugins.cookie import InsecureCookiePlugin
#from repoze.who.plugins.form import FormPlugin
from sqlalchemy.orm.exc import MultipleResultsFound
from repoze.who.plugins.multicompany import auth_tkt
from repoze.who.plugins.multicompany import form
from repoze.who.plugins.multicompany import sa_user_company, sa_userid
from repoze.what.plugins.multicompany import adapters

from repoze.what.middleware import setup_auth


# from repoze.what.plugins.quickstart import setup_sql_auth
# from leanlog_server.lib.auth.plugins import SAUserCompanyAuthenticatorPlugin, \
#        UserCompanyFormPlugin, SAUserCompanyMDPlugin

log = logging.getLogger(__name__)

def add_auth(app, config):
    """
    Add authentication and authorization middleware to the ``app``.

    We're going to define post-login and post-logout pages
    to do some cool things.

    TODO Create a new validation authenticator and challenger that support
    username, password, company

    For documentation on repoze.who and repoze.what, see
    http://docs.repoze.org/who/1.0/
    """
    log.debug("add_auth()")

    log.debug("Configuring repoze.who")
    
    form_plugin = form.make_plugin(
            config.get('repoze.who.login_form_qs'),
            rememberer_name='auth_tkt',
            formcallable='leanlog_server.lib.auth.auth:display_login_form'
            )

    form.classifications = {
            IIdentifier: ['browser'],
            IChallenger: ['browser']
            }

    auth_tkt_plugin = auth_tkt.make_plugin(
            secret=config.get('repoze.who.cookie.secret'),
            secretfile=config.get('repoze.who.cookie.secretfile'),
            cookie_name=config.get('repoze.who.cookie.cookie_name'),
            secure=config.get('repoze.who.cookie.secure'),
            include_ip=config.get('repoze.who.cookie.include_ip'),
            timeout=config.get('repoze.who.cookie.timeout'),
            reissue_time=config.get('repoze.who.cookie.reissue_time'),
            userid_checker='leanlog_server.lib.auth.auth:userid_checker'
            )

    sa_user_company_auth_plugin = sa_user_company.make_plugin(User, Company,
            Session)

    sa_userid_auth_plugin = sa_userid.make_authenticator_plugin(User, Session)

    sa_user_mdprovider_plugin = sa_userid.make_metadata_plugin(User, Session)

    identifiers = [('form', form_plugin), ('auth_tkt', auth_tkt_plugin)]
    authenticators = [('sa_user_compan_auth', sa_user_company_auth_plugin),
            ('sa_userid_auth', sa_userid_auth_plugin)]
    challengers = [('form', form_plugin)]
    mdproviders = [('sa_user', sa_user_mdprovider_plugin)]
   
    from repoze.who.classifiers import default_request_classifier
    from repoze.who.classifiers import default_challenge_decider

    log.debug("Configuring repoze.what")

    acl_plugin = adapters.configure_sql_adapters(
            User, AclGroup, AclPermission, Session,
            group_translations={'section_name': 'id',
                'items': 'users',
                'item_name': 'id',
                'sections': 'groups'},
            permission_translations={'section_name': 'id',
                'items': 'groups',
                'item_name': 'id',
                'sections': 'permissions'}
            )

    log.debug("Initializing middleware: repoze.what and repoze.who")

    return setup_auth(
            app,
            {'all_groups': acl_plugin['group']},
            {'all_permissions': acl_plugin['permission']},
            identifiers=identifiers,
            challengers=challengers,
            authenticators=authenticators,
            mdproviders=mdproviders,
            classifier=default_request_classifier,
            challenge_decider=default_challenge_decider,
            log_stream=log,
            log_level=logging.DEBUG
            )


def userid_checker(userid):
    """
    Verify that the userid is valid
    """

    try:
        user = Session.query(User)\
                .filter(User.id==userid)\
                .filter(User.active==True)\
                .filter(User.deleted==False)\
                .one()

        return (user != None)

    except MultipleResultsFound:
        # More than one user was returned.  Something really bad happened.
        # Don't let the user log in.
        log.debug("Multiple users were found with the userid of {0}".format(userid))
        return False


def display_login_form(environ):
    """
    Render the login form
    """
    from leanlog_server.lib.base import render
    from pylons import tmpl_context as c
    c.dto = {'errors': {},
            'data': {},
            }
    querystring_dict = environ['paste.parsed_dict_querystring'][0] \
            if 'paste.parsed_dict_querystring' in environ \
            and len(environ['paste.parsed_dict_querystring']) > 0 \
            else {}
    c.came_from = querystring_dict['came_from'] \
            if 'came_from' in querystring_dict \
            else environ['PATH_INFO']
    return render('/derived/users/login.mako')





