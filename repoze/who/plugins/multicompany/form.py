# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
# Modifications Copyright (c) 2011 Kris Hardy <kris@sakarta.com>
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

import repoze.who.plugins.form
import urllib

from paste.httpheaders import CONTENT_LENGTH
from paste.httpheaders import CONTENT_TYPE
from paste.httpheaders import LOCATION
from paste.httpexceptions import HTTPFound

from paste.request import parse_dict_querystring
from paste.request import parse_formvars
from paste.request import construct_url

from zope.interface import implements

from repoze.who.config import _resolve
from repoze.who.interfaces import IChallenger
from repoze.who.interfaces import IIdentifier


class FormPluginBase(repoze.who.plugins.form.FormPluginBase):
    pass


class FormPlugin(FormPluginBase):
    """
    A modified implementation of repoze.who.plugins.form.FormPlugin
    """
    implements(IChallenger, IIdentifier)

    def __init__(self, login_form_qs, rememberer_name, 
            formcallable):
        self.login_form_qs = login_form_qs
        # rememberer_name is the name of another configured plugin which
        # implements IIdentifier, to handle remember and forget duties
        # (ala a cookie plugin or a session plugin)
        self.rememberer_name = rememberer_name
        self.formcallable = formcallable

    # IIdentifier
    def identify(self, environ):
        query = parse_dict_querystring(environ)
        # If the extractor finds a special query string on any request,
        # it will attempt to find the values in the input body.
        if query.get(self.login_form_qs): 
            form = parse_formvars(environ)
            from StringIO import StringIO
            # XXX we need to replace wsgi.input because we've read it
            # this smells funny
            environ['wsgi.input'] = StringIO()
            form.update(query)
            try:
                company_name = form['company_name']
                login = form['login']
                password = form['password']
            except KeyError:
                return None
            del query[self.login_form_qs]
            environ['QUERY_STRING'] = urllib.urlencode(query)
            environ['repoze.who.application'] = HTTPFound(
                                                    construct_url(environ))

            credentials = {
                    'company_name': company_name,
                    'login': login,
                    'password': password
                    }

            max_age = form.get('max_age', None)
            if max_age is not None:
                credentials['max_age'] = max_age
            return credentials

        return None

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        if app_headers:
            location = LOCATION(app_headers)
            if location:
                headers = list(app_headers) + list(forget_headers)
                return HTTPFound(headers = headers)
                
        form = self.formcallable(environ)
        def auth_form(environ, start_response):
            content_length = CONTENT_LENGTH.tuples(str(len(form)))
            content_type = CONTENT_TYPE.tuples('text/html')
            headers = content_length + content_type + forget_headers
            start_response('200 OK', headers)
            return [form]

        return auth_form


def make_plugin(login_form_qs,
                rememberer_name,
                formcallable,
               ):
    if rememberer_name is None:
        raise ValueError(
            'must include rememberer key (name of another IIdentifier plugin)')
    if isinstance(formcallable, str):
        formcallable = _resolve(formcallable)
    plugin = FormPlugin(login_form_qs, rememberer_name, formcallable)
    return plugin
