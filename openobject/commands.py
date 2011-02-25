import os
import sys
from optparse import OptionParser

import cherrypy
from cherrypy._cpconfig import as_dict

import openobject
import openobject.release
import openobject.paths

class ConfigurationError(Exception):
    pass

DISTRIBUTION_CONFIG = 'openerp-web.cfg'
def get_config_file():
    if hasattr(sys, 'frozen'):
        configfile = os.path.join(openobject.paths.root(), DISTRIBUTION_CONFIG)
    else:
        setupdir = os.path.dirname(os.path.dirname(__file__))
        isdevdir = os.path.isfile(os.path.join(setupdir, 'setup.py'))
        configfile = '/etc/openerp-web.cfg'
        if isdevdir or not os.path.exists(configfile):
            configfile = os.path.join(setupdir, DISTRIBUTION_CONFIG)
    return configfile

def start():

    parser = OptionParser(version=openobject.release.version)
    parser.add_option("-c", "--config", metavar="FILE", dest="config",
                      help="configuration file", default=get_config_file())
    parser.add_option("-a", "--address", help="host address, overrides server.socket_host")
    parser.add_option("-p", "--port", help="port number, overrides server.socket_port")
    parser.add_option("--no-static", dest="static",
                      action="store_false", default=True,
                      help="Disables serving static files through CherryPy")
    options, args = parser.parse_args(sys.argv)

    if not os.path.exists(options.config):
        raise ConfigurationError(_("Could not find configuration file: %s") %
                                 options.config)
    
    app_config = as_dict(options.config)
    if options.address:
        app_config['global']['server.socket_host'] = options.address
    if options.port:
        try:
            app_config['global']['server.socket_port'] = int(options.port)
        except ValueError:
            pass

    openobject.configure(app_config, enable_static=options.static)

    cherrypy.engine.start()
    cherrypy.engine.block()
