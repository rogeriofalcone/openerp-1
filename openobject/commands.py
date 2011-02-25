import sys
from optparse import OptionParser

import cherrypy

import openobject
import openobject.config
import openobject.release
import openobject.paths

def start():
    parser = OptionParser(version=openobject.release.version)
    parser.add_option("-c", "--config", metavar="FILE", dest="config",
                      help="configuration file", default=None)
    parser.add_option("-a", "--address", help="host address, overrides server.socket_host")
    parser.add_option("-p", "--port", help="port number, overrides server.socket_port")
    parser.add_option("--no-static", dest="static",
                      action="store_false", default=True,
                      help="Disables serving static files through CherryPy")
    options, args = parser.parse_args(sys.argv)
    
    overrides = {'global': {}}
    if options.address:
        overrides['global']['server.socket_host'] = options.address
    if options.port:
        try:
            overrides['global']['server.socket_port'] = int(options.port)
        except ValueError:
            pass

    try:
        openobject.configure(options.config, enable_static=options.static,
                             **overrides)
    except openobject.config.ConfigurationError, e:
        parser.error(e.args[0])

    cherrypy.engine.start()
    cherrypy.engine.block()
