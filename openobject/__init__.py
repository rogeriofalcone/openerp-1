import logging
import os
import sys

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')
if os.path.exists(libdir) and libdir not in sys.path:
    sys.path.insert(0, libdir)

import cherrypy
import openobject
import openobject.config
import openobject.controllers
import openobject.widgets

__all__ = ['ustr', 'application', 'configure', 'enable_static_paths',
           'WSGI_STATIC_PATHS']

# handle static files & paths via the WSGI server
# (using cherrypy's tools.staticfile and tools.staticdir)
WSGI_STATIC_PATHS = False

def ustr(value):
    """This method is similar to the builtin `str` method, except
    it will return Unicode string.

    @param value: the value to convert

    @rtype: unicode
    @return: unicode string
    """

    if isinstance(value, unicode):
        return value

    if hasattr(value, "__unicode__"):
        return unicode(value)

    try: # first try without encoding
        return unicode(value)
    except:
        pass

    try: # then try with utf-8
        return unicode(value, 'utf-8')
    except:
        pass

    try: # then try with extened iso-8858
        return unicode(value, 'iso-8859-15')
    except:
        pass

    try:
        return ustr(str(value))
    except:
        return " ".join([ustr(s) for s in value])

__builtins__['ustr'] = ustr

import i18n
i18n.install()

application = cherrypy.tree.mount(None)
def enable_static_paths():
    ''' Enables handling of static paths by CherryPy:
    * /openobject/static
    * /favicon.ico
    * LICENSE.txt
    '''
    global WSGI_STATIC_PATHS
    if WSGI_STATIC_PATHS: return
    WSGI_STATIC_PATHS = True

    static_dir = os.path.abspath(
            openobject.paths.root('openobject', 'static'))
    application.merge(
        {'/openobject/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': static_dir
        }, '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(static_dir,
                                                      "images", "favicon.ico")
        }, '/LICENSE.txt': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(static_dir, '..', '..',
                                                      'doc', 'LICENSE.txt')
    }})

BASE_GLOBAL = {
    'tools.sessions.on': True,
    'tools.csrf.on': True,
    # Conversion of input parameters via formencode.variabledecode.NestedVariables
    'tools.nestedvars.on': True,
    'tools.web_modules.on': True,
    'tools.fix_custom_headers_redirection.on': True,
    'tools.fix_custom_headers_redirection.custom_headers': [
        # Header set by XHR requests, used to know whether the client needs
        # a full template (including JS and CSS files) or just the content
        # area of the HTML
        ('X-Requested-With', 'requested_with')
    ],
    'tools.clear_cache_buster.on': True,
    'tools.openobject_dispatcher.on': True,

    'tools.log_traceback.on': False,
    'tools.cgitb.on': True
}
BASE_APP = {
    'openerp.server.timeout': 450
}
def configure(config, enable_static=False):
    ''' Configures OpenERP Web Client.

    Takes a CherryPy configuration with two sections (``global``
    and ``openerp-web``)

    :param config: a configuration file path, a configuration file or a
                       configuration dict (anything which can be used by
                       ``cherrypy._cpconfig.as_dict``, really).
    :type config: ``str | < read :: () -> str > | dict``
    :param enable_static: configure CherryPy to handle the distribution of
                          static resources by itself (via static tools)
    :type enable_static: ``bool``
    :return: ``None``
    '''
    # global config
    cherrypy.config.update(
        BASE_GLOBAL)
    cherrypy.config.update(
        config.pop('global', {}))

    application.merge({'openerp-web': BASE_APP})
    application.merge(config)

    # logging config
    error_level = logging._levelNames.get(
        cherrypy.config.get('log.error_level'), 'WARNING')
    access_level = logging._levelNames.get(
        cherrypy.config.get('log.access_level'), 'INFO')

    cherrypy.log.error_log.setLevel(error_level)
    cherrypy.log.access_log.setLevel(access_level)

    openobject.config.configure_babel()
    if enable_static:
        enable_static_paths()
