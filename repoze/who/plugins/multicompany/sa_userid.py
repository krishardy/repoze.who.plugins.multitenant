from zope.interface import implements
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from repoze.who.interfaces import IAuthenticator, IMetadataProvider


class _BaseSQLAlchemyPlugin(object):
    """
    repoze.who plugin base
    """
    def __init__(self, user_class, dbsession):
        self.user_class = user_class
        self.dbsession = dbsession

    def get_user(self, userid):
        # A fresh transaction must be used to avoid using an invalid one. It's
        # therefore assumed that at this point it must've been successfully
        # committed or rolled back.
        self.dbsession.remove()
        
        query = self.dbsession.query(self.user_class)
        query = query.filter(self.user_class.id==userid)
        
        try:
            return query.one()
        except (NoResultFound, MultipleResultsFound):
            # As recommended in the docs for repoze.who, it's important to
            # verify that there's only _one_ matching userid.
            return None


class SQLAlchemyAuthenticatorPlugin(_BaseSQLAlchemyPlugin):
    """
    repoze.who authenticator plugin
    """

    implements(IAuthenticator)

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        try:
           userid = identity['userid']
           password = identity['password']
        except KeyError:
            return None

        user = self.get_user(userid)

        if user and user.validate_password(password):
            return userid


def make_authenticator_plugin(user_class, dbsession):
    if user_class is None:
        raise ValueError('user_class cannot be None')
    if dbsession is None:
        raise ValueError('dbsession cannot be None')
    return SQLAlchemyAuthenticatorPlugin(user_class, dbsession)


class SQLAlchemyUserMDPlugin(_BaseSQLAlchemyPlugin):
    """
    :mod:`repoze.who` metadata provider that loads the SQLAlchemy-powered
    object for the current user.
    
    It loads the object into ``identity['user']``.
    
    Example::
    
        from repoze.who.plugins.sa import SQLAlchemyUserMDPlugin
        from yourcoolproject.model import User, DBSession
        
        mdprovider = SQLAlchemyUserMDPlugin(User, DBSession)
    
    This plugin assumes that the user name is kept in the ``user_name``
    attribute of the users' class. If you don't want to call the attribute
    above as ``user_name``, then you have to "translate" it as in the sample 
    below::
    
        # You have User.username instead of User.user_name:
        mdprovider.translations['user_name'] = 'username'
    
    .. note::
    
        If you want to configure this plugin from an ``ini`` file, use
        :func:`make_sa_user_mdprovider`.
    
    """
    
    implements(IMetadataProvider)
    
    def add_metadata(self, environ, identity):
        identity['user'] = self.get_user(identity['repoze.who.userid'])


def make_metadata_plugin(user_class, dbsession):
    return SQLAlchemyUserMDPlugin(user_class, dbsession)
