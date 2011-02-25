import sys
from optparse import OptionParser

import cherrypy

import openobject
import openobject.config
import openobject.release
import openobject.paths

def loglevel(option, str_opt, value, parser):
    if ':' not in value:
        parser.values.log.append((value, 'DEBUG'))
        return
    logger, level = value.rsplit(':', 1)
    if level.isdigit():
        level = int(level)
    parser.values.log.append((logger, level))

def start():
    parser = OptionParser(version=openobject.release.version)
    parser.add_option("-c", "--config", metavar="FILE",
                      help="configuration file", default=None)
    parser.add_option("-a", "--address", help="host address, overrides server.socket_host")
    parser.add_option("-p", "--port", help="port number, overrides server.socket_port")
    parser.add_option("--logging-config", metavar="FILE",
                      help="path to a configuration file for Python's "
                           "logging module, will be used to configure "
                           "the web client's logging")
    parser.add_option('-l', '--log', metavar='LOGGER[:LEVEL=DEBUG]', default=[],
                      action="callback", callback=loglevel, type="str",
                      help="Fast logger configuration: changes the logging "
                           "level of the provided logger. This option can be "
                           "called several times to set up multiple loggers.")
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
        openobject.configure(options.config,
                             enable_static=options.static,
                             logging_configuration=options.logging_config,
                             loggers=dict(options.log),
                             **overrides)
    except openobject.config.ConfigurationError, e:
        parser.error(e.args[0])

    cherrypy.engine.start()
    cherrypy.engine.block()
