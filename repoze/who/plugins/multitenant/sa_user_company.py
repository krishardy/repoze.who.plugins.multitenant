from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


class SQLAlchemyPlugin(object):
    """
    repoze.who authenticator plugin
    """

    def __init__(self, user_class, company_class, dbsession):
        self.user_class = user_class
        self.company_class = company_class
        self.dbsession = dbsession

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        try:
           company_name = identity['company_name']
           login = identity['login']
           password = identity['password']
        except KeyError:
            return None

        try:
            company = self.dbsession.query(self.company_class)\
                    .filter(self.company_class.name==company_name)\
                    .filter(self.company_class.active==True)\
                    .one()
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None

        if company == None:
            return None
        
        try:
            user = self.dbsession.query(self.user_class)\
                    .filter(self.user_class.username==login)\
                    .filter(self.user_class.company_id==company.id)\
                    .filter(self.user_class.active==True)\
                    .filter(self.user_class.deleted==False)\
                    .one()
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None

        if user == None or user.validate_password(password) == False:
            return None

        return user.id


def make_plugin(user_class, company_class, dbsession):
    if user_class is None:
        raise ValueError('user_class cannot be None')
    if company_class is None:
        raise ValueError('company_class cannot be None')
    if dbsession is None:
        raise ValueError('dbsession cannot be None')
    return SQLAlchemyPlugin(user_class, company_class, dbsession)
