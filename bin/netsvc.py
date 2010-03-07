#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    The refactoring about the OpenSSL support come from Tryton
#    Copyright (C) 2007-2009 Cédric Krier.
#    Copyright (C) 2007-2009 Bertrand Chenal.
#    Copyright (C) 2008 B2CK SPRL.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import logging.handlers
import sys
import threading
import time
import release
from pprint import pformat
import warnings

class Service(object):
    """ Base class for *Local* services

        Functionality here is trusted, no authentication.
    """
    _services = {}
    def __init__(self, name, audience=''):
        Service._services[name] = self
        self.__name = name
        self._methods = {}

    def joinGroup(self, name):
        raise Exception("No group for local services")
        #GROUPS.setdefault(name, {})[self.__name] = self

    @classmethod
    def exists(cls, name):
        return name in cls._services

    @classmethod
    def remove(cls, name):
        if cls.exists(name):
            cls._services.pop(name)

    def exportMethod(self, method):
        if callable(method):
            self._methods[method.__name__] = method

    def abortResponse(self, error, description, origin, details):
        if not tools.config['debug_mode']:
            raise Exception("%s -- %s\n\n%s"%(origin, description, details))
        else:
            raise

class LocalService(object):
    """ Proxy for local services. 
    
        Any instance of this class will behave like the single instance
        of Service(name)
    """
    __logger = logging.getLogger('service')
    def __init__(self, name):
        self.__name = name
        try:
            self._service = Service._services[name]
            for method_name, method_definition in self._service._methods.items():
                setattr(self, method_name, method_definition)
        except KeyError, keyError:
            self.__logger.error('This service does not exist: %s' % (str(keyError),) )
            raise

    def __call__(self, method, *params):
        return getattr(self, method)(*params)

class ExportService(object):
    """ Proxy for exported services. 

    All methods here should take an AuthProxy as their first parameter. It
    will be appended by the calling framework.

    Note that this class has no direct proxy, capable of calling 
    eservice.method(). Rather, the proxy should call 
    dispatch(method,auth,params)
    """
    
    _services = {}
    _groups = {}
    
    def __init__(self, name, audience=''):
        ExportService._services[name] = self
        self.__name = name

    def joinGroup(self, name):
        ExportService._groups.setdefault(name, {})[self.__name] = self

    @classmethod
    def getService(cls,name):
        return cls._services[name]

    def dispatch(self, method, auth, params):
        raise Exception("stub dispatch at %s" % self.__name)
        
    def new_dispatch(self,method,auth,params):
        raise Exception("stub dispatch at %s" % self.__name)

    def abortResponse(self, error, description, origin, details):
        if not tools.config['debug_mode']:
            raise Exception("%s -- %s\n\n%s"%(origin, description, details))
        else:
            raise

LOG_NOTSET = 'notset'
LOG_DEBUG_RPC = 'debug_rpc'
LOG_DEBUG = 'debug'
LOG_TEST = 'test'
LOG_INFO = 'info'
LOG_WARNING = 'warn'
LOG_ERROR = 'error'
LOG_CRITICAL = 'critical'

logging.DEBUG_RPC = logging.DEBUG - 2
logging.addLevelName(logging.DEBUG_RPC, 'DEBUG_RPC')

logging.TEST = logging.INFO - 5
logging.addLevelName(logging.TEST, 'TEST')

def init_logger():
    import os
    from tools.translate import resetlocale
    resetlocale()

    logger = logging.getLogger()
    # create a format for log messages and dates
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s')

    if tools.config['syslog']:
        # SysLog Handler
        if os.name == 'nt':
            handler = logging.handlers.NTEventLogHandler("%s %s" %
                                                         (release.description,
                                                          release.version))
        else:
            handler = logging.handlers.SysLogHandler('/dev/log')
        formatter = logging.Formatter("%s %s" % (release.description, release.version) + ':%(levelname)s:%(name)s:%(message)s')

    elif tools.config['logfile']:
        # LogFile Handler
        logf = tools.config['logfile']
        try:
            dirname = os.path.dirname(logf)
            if dirname and not os.path.isdir(dirname):
                os.makedirs(dirname)
            if tools.config['logrotate'] is not False:
                handler = logging.handlers.TimedRotatingFileHandler(logf,'D',1,30)
            elif os.name == 'posix':
                handler = logging.handlers.WatchedFileHandler(logf)
            else:
                handler = logging.handlers.FileHandler(logf)
        except Exception, ex:
            sys.stderr.write("ERROR: couldn't create the logfile directory. Logging to the standard output.\n")
            handler = logging.StreamHandler(sys.stdout)
    else:
        # Normal Handler on standard output
        handler = logging.StreamHandler(sys.stdout)


    # tell the handler to use this format
    handler.setFormatter(formatter)

    # add the handler to the root logger
    logger.addHandler(handler)
    logger.setLevel(int(tools.config['log_level'] or '0'))

    if (not isinstance(handler, logging.FileHandler)) and os.name != 'nt':
        # change color of level names
        # uses of ANSI color codes
        # see http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html
        # maybe use http://code.activestate.com/recipes/574451/
        colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', None, 'default']
        foreground = lambda f: 30 + colors.index(f)
        background = lambda f: 40 + colors.index(f)

        mapping = {
            'DEBUG_RPC': ('blue', 'white'),
            'DEBUG': ('blue', 'default'),
            'INFO': ('green', 'default'),
            'TEST': ('white', 'blue'),
            'WARNING': ('yellow', 'default'),
            'ERROR': ('red', 'default'),
            'CRITICAL': ('white', 'red'),
        }

        for level, (fg, bg) in mapping.items():
            msg = "\x1b[%dm\x1b[%dm%s\x1b[0m" % (foreground(fg), background(bg), level)
            logging.addLevelName(getattr(logging, level), msg)


class Logger(object):
    def __init__(self):
        warnings.warn("The netsvc.Logger API shouldn't be used anymore, please "
                      "use the standard `logging.getLogger` API instead",
                      PendingDeprecationWarning, stacklevel=2)
        super(Logger, self).__init__()

    def notifyChannel(self, name, level, msg):
        warnings.warn("notifyChannel API shouldn't be used anymore, please use "
                      "the standard `logging` module instead",
                      PendingDeprecationWarning, stacklevel=2)
        from service.web_services import common

        log = logging.getLogger(tools.ustr(name))

        if level in [LOG_DEBUG_RPC, LOG_TEST] and not hasattr(log, level):
            fct = lambda msg, *args, **kwargs: log.log(getattr(logging, level.upper()), msg, *args, **kwargs)
            setattr(log, level, fct)


        level_method = getattr(log, level)

        if isinstance(msg, Exception):
            msg = tools.exception_to_unicode(msg)

        try:
            msg = tools.ustr(msg).strip()
            if level in (LOG_ERROR, LOG_CRITICAL) and tools.config.get_misc('debug','env_info',False):
                msg = common().exp_get_server_environment() + "\n" + msg

            result = msg.split('\n')
        except UnicodeDecodeError:
            result = msg.strip().split('\n')
        try:
            if len(result)>1:
                for idx, s in enumerate(result):
                    level_method('[%02d]: %s' % (idx+1, s,))
            elif result:
                level_method(result[0])
        except IOError,e:
            # TODO: perhaps reset the logger streams?
            #if logrotate closes our files, we end up here..
            pass
        except:
            # better ignore the exception and carry on..
            pass

    def set_loglevel(self, level):
        log = logging.getLogger()
        log.setLevel(logging.INFO) # make sure next msg is printed
        log.info("Log level changed to %s" % logging.getLevelName(level))
        log.setLevel(level)

    def shutdown(self):
        logging.shutdown()

import tools
init_logger()

class Agent(object):
    _timers = {}
    _logger = Logger()

    __logger = logging.getLogger('timer')

    def setAlarm(self, fn, dt, db_name, *args, **kwargs):
        wait = dt - time.time()
        if wait > 0:
            self.__logger.debug("Job scheduled in %.3g seconds for %s.%s" % (wait, fn.im_class.__name__, fn.func_name))
            timer = threading.Timer(wait, fn, args, kwargs)
            timer.start()
            self._timers.setdefault(db_name, []).append(timer)

        for db in self._timers:
            for timer in self._timers[db]:
                if not timer.isAlive():
                    self._timers[db].remove(timer)

    @classmethod
    def cancel(cls, db_name):
        """Cancel all timers for a given database. If None passed, all timers are cancelled"""
        for db in cls._timers:
            if db_name is None or db == db_name:
                for timer in cls._timers[db]:
                    timer.cancel()

    @classmethod
    def quit(cls):
        cls.cancel(None)

import traceback

class Server:
    """ Generic interface for all servers with an event loop etc.
        Override this to impement http, net-rpc etc. servers.

        Servers here must have threaded behaviour. start() must not block,
        there is no run().
    """
    __is_started = False
    __servers = []


    __logger = logging.getLogger('server')

    def __init__(self):
        if Server.__is_started:
            raise Exception('All instances of servers must be inited before the startAll()')
        Server.__servers.append(self)

    def start(self):
        self.__logger.debug("called stub Server.start")

    def stop(self):
        self.__logger.debug("called stub Server.stop")

    def stats(self):
        """ This function should return statistics about the server """
        return "%s: No statistics" % str(self.__class__)

    @classmethod
    def startAll(cls):
        if cls.__is_started:
            return
        cls.__logger.info("Starting %d services" % len(cls.__servers))
        for srv in cls.__servers:
            srv.start()
        cls.__is_started = True

    @classmethod
    def quitAll(cls):
        if not cls.__is_started:
            return
        cls.__logger.info("Stopping %d services" % len(cls.__servers))
        for srv in cls.__servers:
            srv.stop()
        cls.__is_started = False

    @classmethod
    def allStats(cls):
        res = ["Servers %s" % ('stopped', 'started')[cls.__is_started]]
        res.extend(srv.stats() for srv in cls.__servers)
        return '\n'.join(res)

class OpenERPDispatcherException(Exception):
    def __init__(self, exception, traceback):
        self.exception = exception
        self.traceback = traceback

class OpenERPDispatcher:
    def log(self, title, msg):
        Logger().notifyChannel('%s' % title, LOG_DEBUG_RPC, pformat(msg))

    def dispatch(self, service_name, method, params):
        try:
            self.log('service', service_name)
            self.log('method', method)
            self.log('params', params)
            auth = getattr(self, 'auth_provider', None)
            result = ExportService.getService(service_name).dispatch(method, auth, params)
            self.log('result', result)
            # We shouldn't marshall None,
            if result == None:
                result = False
            return result
        except Exception, e:
            self.log('exception', tools.exception_to_unicode(e))
            tb = getattr(e, 'traceback', sys.exc_info())
            tb_s = "".join(traceback.format_exception(*tb))
            if tools.config['debug_mode']:
                import pdb
                pdb.post_mortem(tb[2])
            raise OpenERPDispatcherException(e, tb_s)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
