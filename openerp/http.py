# -*- coding: utf-8 -*-
#----------------------------------------------------------
# OpenERP HTTP layer
#----------------------------------------------------------
import ast
import collections
import contextlib
import errno
import functools
import getpass
import inspect
import logging
import mimetypes
import os
import random
import re
import sys
import tempfile
import threading
import time
import traceback
import urlparse
import warnings

import babel.core
import psutil
import psycopg2
import simplejson
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi

import openerp
from openerp.service import security, model as service_model
from openerp.tools.func import lazy_property

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# RequestHandler
#----------------------------------------------------------
# Thread local global request object
_request_stack = werkzeug.local.LocalStack()

request = _request_stack()
"""
    A global proxy that always redirect to the current request object.
"""

def replace_request_password(args):
    # password is always 3rd argument in a request, we replace it in RPC logs
    # so it's easier to forward logs for diagnostics/debugging purposes...
    if len(args) > 2:
        args = list(args)
        args[2] = '*'
    return tuple(args)

def dispatch_rpc(service_name, method, params):
    """ Handle a RPC call.

    This is pure Python code, the actual marshalling (from/to XML-RPC) is done
    in a upper layer.
    """
    try:
        rpc_request = logging.getLogger(__name__ + '.rpc.request')
        rpc_response = logging.getLogger(__name__ + '.rpc.response')
        rpc_request_flag = rpc_request.isEnabledFor(logging.DEBUG)
        rpc_response_flag = rpc_response.isEnabledFor(logging.DEBUG)
        if rpc_request_flag or rpc_response_flag:
            start_time = time.time()
            start_rss, start_vms = 0, 0
            start_rss, start_vms = psutil.Process(os.getpid()).get_memory_info()
            if rpc_request and rpc_response_flag:
                openerp.netsvc.log(rpc_request, logging.DEBUG, '%s.%s' % (service_name, method), replace_request_password(params))

        threading.current_thread().uid = None
        threading.current_thread().dbname = None
        if service_name == 'common':
            dispatch = openerp.service.common.dispatch
        elif service_name == 'db':
            dispatch = openerp.service.db.dispatch
        elif service_name == 'object':
            dispatch = openerp.service.model.dispatch
        elif service_name == 'report':
            dispatch = openerp.service.report.dispatch
        else:
            dispatch = openerp.service.wsgi_server.rpc_handlers.get(service_name)
        result = dispatch(method, params)

        if rpc_request_flag or rpc_response_flag:
            end_time = time.time()
            end_rss, end_vms = 0, 0
            end_rss, end_vms = psutil.Process(os.getpid()).get_memory_info()
            logline = '%s.%s time:%.3fs mem: %sk -> %sk (diff: %sk)' % (service_name, method, end_time - start_time, start_vms / 1024, end_vms / 1024, (end_vms - start_vms)/1024)
            if rpc_response_flag:
                openerp.netsvc.log(rpc_response, logging.DEBUG, logline, result)
            else:
                openerp.netsvc.log(rpc_request, logging.DEBUG, logline, replace_request_password(params), depth=1)

        return result
    except (openerp.osv.orm.except_orm, openerp.exceptions.AccessError, \
            openerp.exceptions.AccessDenied, openerp.exceptions.Warning, \
            openerp.exceptions.RedirectWarning):
        raise
    except openerp.exceptions.DeferredException, e:
        _logger.exception(openerp.tools.exception_to_unicode(e))
        openerp.tools.debugger.post_mortem(openerp.tools.config, e.traceback)
        raise
    except Exception, e:
        _logger.exception(openerp.tools.exception_to_unicode(e))
        openerp.tools.debugger.post_mortem(openerp.tools.config, sys.exc_info())
        raise

def local_redirect(path, query=None, keep_hash=False, forward_debug=True, code=303):
    url = path
    if not query:
        query = {}
    if forward_debug and request and request.debug:
        query['debug'] = None
    if query:
        url += '?' + werkzeug.url_encode(query)
    if keep_hash:
        return redirect_with_hash(url, code)
    else:
        return werkzeug.utils.redirect(url, code)

def redirect_with_hash(url, code=303):
    # Most IE and Safari versions decided not to preserve location.hash upon
    # redirect. And even if IE10 pretends to support it, it still fails
    # inexplicably in case of multiple redirects (and we do have some).
    # See extensive test page at http://greenbytes.de/tech/tc/httpredirects/
    if request.httprequest.user_agent.browser in ('firefox',):
        return werkzeug.utils.redirect(url, code)
    return "<html><head><script>window.location = '%s' + location.hash;</script></head></html>" % url

class WebRequest(object):
    """ Parent class for all OpenERP Web request types, mostly deals with
    initialization and setup of the request object (the dispatching itself has
    to be handled by the subclasses)

    :param request: a wrapped werkzeug Request object
    :type request: :class:`werkzeug.wrappers.BaseRequest`

    .. attribute:: httprequest

        the original :class:`werkzeug.wrappers.Request` object provided to the
        request

    .. attribute:: httpsession

        .. deprecated:: 8.0

        Use ``self.session`` instead.

    .. attribute:: params

        :class:`~collections.Mapping` of request parameters, not generally
        useful as they're provided directly to the handler method as keyword
        arguments

    .. attribute:: session_id

        opaque identifier for the :class:`session.OpenERPSession` instance of
        the current request

    .. attribute:: session

        a :class:`OpenERPSession` holding the HTTP session data for the
        current http session

    .. attribute:: context

        :class:`~collections.Mapping` of context values for the current request

    .. attribute:: db

        ``str``, the name of the database linked to the current request. Can be ``None``
        if the current request uses the ``none`` authentication.

    .. attribute:: uid

        ``int``, the id of the user related to the current request. Can be ``None``
        if the current request uses the ``none`` authenticatoin.
    """
    def __init__(self, httprequest):
        self.httprequest = httprequest
        self.httpresponse = None
        self.httpsession = httprequest.session
        self.session = httprequest.session
        self.session_id = httprequest.session.sid
        self.disable_db = False
        self.uid = None
        self.endpoint = None
        self.auth_method = None
        self._cr_cm = None
        self._cr = None

        # prevents transaction commit, use when you catch an exception during handling
        self._failed = None

        # set db/uid trackers - they're cleaned up at the WSGI
        # dispatching phase in openerp.service.wsgi_server.application
        if self.db:
            threading.current_thread().dbname = self.db
        if self.session.uid:
            threading.current_thread().uid = self.session.uid
        self.context = dict(self.session.context)
        self.lang = self.context["lang"]

    @property
    def registry(self):
        """
        The registry to the database linked to this request. Can be ``None`` if the current request uses the
        ``none'' authentication.
        """
        return openerp.modules.registry.RegistryManager.get(self.db) if self.db else None

    @property
    def db(self):
        """
        The registry to the database linked to this request. Can be ``None`` if the current request uses the
        ``none'' authentication.
        """
        return self.session.db if not self.disable_db else None

    @property
    def cr(self):
        """
        The cursor initialized for the current method call. If the current request uses the ``none`` authentication
        trying to access this property will raise an exception.
        """
        # some magic to lazy create the cr
        if not self._cr:
            # Test cursors
            self._cr = openerp.tests.common.acquire_test_cursor(self.session_id)
            if not self._cr:
                self._cr = self.registry.db.cursor()
        return self._cr

    def __enter__(self):
        _request_stack.push(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _request_stack.pop()

        if self._cr:
            # Dont close test cursors
            if not openerp.tests.common.release_test_cursor(self._cr):
                if exc_type is None and not self._failed:
                    self._cr.commit()
                else:
                    # just to be explicit - happens at close() anyway
                    self._cr.rollback()
                self._cr.close()
        # just to be sure no one tries to re-use the request
        self.disable_db = True
        self.uid = None

    def set_handler(self, endpoint, arguments, auth):
        # is this needed ?
        arguments = dict((k, v) for k, v in arguments.iteritems()
                         if not k.startswith("_ignored_"))

        endpoint.arguments = arguments
        self.endpoint = endpoint
        self.auth_method = auth

    def _call_function(self, *args, **kwargs):
        request = self
        if self.endpoint.routing['type'] != self._request_type:
            raise Exception("%s, %s: Function declared as capable of handling request of type '%s' but called with a request of type '%s'" \
                % (self.endpoint.original, self.httprequest.path, self.endpoint.routing['type'], self._request_type))

        kwargs.update(self.endpoint.arguments)

        # Backward for 7.0
        if self.endpoint.first_arg_is_req:
            args = (request,) + args

        # Correct exception handling and concurency retry
        @service_model.check
        def checked_call(___dbname, *a, **kw):
            # The decorator can call us more than once if there is an database error. In this
            # case, the request cursor is unusable. Rollback transaction to create a new one.
            if self._cr and not openerp.tools.config['test_enable']:
                self._cr.rollback()
            return self.endpoint(*a, **kw)

        if self.db:
            return checked_call(self.db, *args, **kwargs)
        return self.endpoint(*args, **kwargs)

    @property
    def debug(self):
        return 'debug' in self.httprequest.args

    @contextlib.contextmanager
    def registry_cr(self):
        warnings.warn('please use request.registry and request.cr directly', DeprecationWarning)
        yield (self.registry, self.cr)

def route(route=None, **kw):
    """
    Decorator marking the decorated method as being a handler for requests. The method must be part of a subclass
    of ``Controller``.

    :param route: string or array. The route part that will determine which http requests will match the decorated
    method. Can be a single string or an array of strings. See werkzeug's routing documentation for the format of
    route expression ( http://werkzeug.pocoo.org/docs/routing/ ).
    :param type: The type of request, can be ``'http'`` or ``'json'``.
    :param auth: The type of authentication method, can on of the following:

        * ``user``: The user must be authenticated and the current request will perform using the rights of the
        user.
        * ``admin``: The user may not be authenticated and the current request will perform using the admin user.
        * ``none``: The method is always active, even if there is no database. Mainly used by the framework and
        authentication modules. There request code will not have any facilities to access the database nor have any
        configuration indicating the current database nor the current user.
    :param methods: A sequence of http methods this route applies to. If not specified, all methods are allowed.
    :param cors: The Access-Control-Allow-Origin cors directive value.
    """
    routing = kw.copy()
    assert not 'type' in routing or routing['type'] in ("http", "json")
    def decorator(f):
        if route:
            if isinstance(route, list):
                routes = route
            else:
                routes = [route]
            routing['routes'] = routes
        @functools.wraps(f)
        def response_wrap(*args, **kw):
            response = f(*args, **kw)
            if isinstance(response, Response) or f.routing_type == 'json':
                return response
            elif isinstance(response, werkzeug.wrappers.BaseResponse):
                response = Response.force_type(response)
                response.set_default()
                return response
            elif isinstance(response, basestring):
                return Response(response)
            else:
                _logger.warn("<function %s.%s> returns an invalid response type for an http request" % (f.__module__, f.__name__))
            return response
        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap
    return decorator

class JsonRequest(WebRequest):
    """ JSON-RPC2 over HTTP.

    Sucessful request::

      --> {"jsonrpc": "2.0",
           "method": "call",
           "params": {"context": {},
                      "arg1": "val1" },
           "id": null}

      <-- {"jsonrpc": "2.0",
           "result": { "res1": "val1" },
           "id": null}

    Request producing a error::

      --> {"jsonrpc": "2.0",
           "method": "call",
           "params": {"context": {},
                      "arg1": "val1" },
           "id": null}

      <-- {"jsonrpc": "2.0",
           "error": {"code": 1,
                     "message": "End user error message.",
                     "data": {"code": "codestring",
                              "debug": "traceback" } },
           "id": null}

    """
    _request_type = "json"

    def __init__(self, *args):
        super(JsonRequest, self).__init__(*args)

        self.jsonp_handler = None

        args = self.httprequest.args
        jsonp = args.get('jsonp')
        self.jsonp = jsonp
        request = None
        request_id = args.get('id')
        
        if jsonp and self.httprequest.method == 'POST':
            # jsonp 2 steps step1 POST: save call
            def handler():
                self.session['jsonp_request_%s' % (request_id,)] = self.httprequest.form['r']
                self.session.modified = True
                headers=[('Content-Type', 'text/plain; charset=utf-8')]
                r = werkzeug.wrappers.Response(request_id, headers=headers)
                return r
            self.jsonp_handler = handler
            return
        elif jsonp and args.get('r'):
            # jsonp method GET
            request = args.get('r')
        elif jsonp and request_id:
            # jsonp 2 steps step2 GET: run and return result
            request = self.session.pop('jsonp_request_%s' % (request_id,), '{}')
        else:
            # regular jsonrpc2
            request = self.httprequest.stream.read()

        # Read POST content or POST Form Data named "request"
        self.jsonrequest = simplejson.loads(request)
        self.params = dict(self.jsonrequest.get("params", {}))
        self.context = self.params.pop('context', dict(self.session.context))

    def dispatch(self):
        """ Calls the method asked for by the JSON-RPC2 or JSONP request
        """
        if self.jsonp_handler:
            return self.jsonp_handler()
        response = {"jsonrpc": "2.0" }
        error = None

        try:
            response['id'] = self.jsonrequest.get('id')
            response["result"] = self._call_function(**self.params)
        except AuthenticationError, e:
            _logger.exception("JSON-RPC AuthenticationError in %s.", self.httprequest.path)
            se = serialize_exception(e)
            error = {
                'code': 100,
                'message': "OpenERP Session Invalid",
                'data': se
            }
            self._failed = e # prevent tx commit
        except Exception, e:
            # Mute test cursor error for runbot
            if not (openerp.tools.config['test_enable'] and isinstance(e, psycopg2.OperationalError)):
                _logger.exception("JSON-RPC Exception in %s.", self.httprequest.path)
            se = serialize_exception(e)
            error = {
                'code': 200,
                'message': "OpenERP Server Error",
                'data': se
            }
            self._failed = e # prevent tx commit
        if error:
            response["error"] = error

        if self.jsonp:
            # If we use jsonp, that's mean we are called from another host
            # Some browser (IE and Safari) do no allow third party cookies
            # We need then to manage http sessions manually.
            response['session_id'] = self.session_id
            mime = 'application/javascript'
            body = "%s(%s);" % (self.jsonp, simplejson.dumps(response),)
        else:
            mime = 'application/json'
            body = simplejson.dumps(response)

        r = Response(body, headers=[('Content-Type', mime), ('Content-Length', len(body))])
        return r

def serialize_exception(e):
    tmp = {
        "name": type(e).__module__ + "." + type(e).__name__ if type(e).__module__ else type(e).__name__,
        "debug": traceback.format_exc(),
        "message": u"%s" % e,
        "arguments": to_jsonable(e.args),
    }
    if isinstance(e, openerp.osv.osv.except_osv):
        tmp["exception_type"] = "except_osv"
    elif isinstance(e, openerp.exceptions.Warning):
        tmp["exception_type"] = "warning"
    elif isinstance(e, openerp.exceptions.AccessError):
        tmp["exception_type"] = "access_error"
    elif isinstance(e, openerp.exceptions.AccessDenied):
        tmp["exception_type"] = "access_denied"
    return tmp

def to_jsonable(o):
    if isinstance(o, str) or isinstance(o,unicode) or isinstance(o, int) or isinstance(o, long) \
        or isinstance(o, bool) or o is None or isinstance(o, float):
        return o
    if isinstance(o, list) or isinstance(o, tuple):
        return [to_jsonable(x) for x in o]
    if isinstance(o, dict):
        tmp = {}
        for k, v in o.items():
            tmp[u"%s" % k] = to_jsonable(v)
        return tmp
    return u"%s" % o

def jsonrequest(f):
    """ 
        .. deprecated:: 8.0

        Use the ``route()`` decorator instead.
    """
    base = f.__name__.lstrip('/')
    if f.__name__ == "index":
        base = ""
    return route([base, base + "/<path:_ignored_path>"], type="json", auth="user", combine=True)(f)

class HttpRequest(WebRequest):
    """ Regular GET/POST request
    """
    _request_type = "http"

    def __init__(self, *args):
        super(HttpRequest, self).__init__(*args)
        params = self.httprequest.args.to_dict()
        params.update(self.httprequest.form.to_dict())
        params.update(self.httprequest.files.to_dict())
        params.pop('session_id', None)
        self.params = params

    def dispatch(self):
        if request.httprequest.method == 'OPTIONS' and request.endpoint and request.endpoint.routing.get('cors'):
            headers = {
                'Access-Control-Max-Age': 60 * 60 * 24,
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
            }
            return Response(status=200, headers=headers)

        r = self._call_function(**self.params)
        if not r:
            r = Response(status=204)  # no content
        return r

    def make_response(self, data, headers=None, cookies=None):
        """ Helper for non-HTML responses, or HTML responses with custom
        response headers or cookies.

        While handlers can just return the HTML markup of a page they want to
        send as a string if non-HTML data is returned they need to create a
        complete response object, or the returned data will not be correctly
        interpreted by the clients.

        :param basestring data: response body
        :param headers: HTTP headers to set on the response
        :type headers: ``[(name, value)]``
        :param collections.Mapping cookies: cookies to set on the client
        """
        response = Response(data, headers=headers)
        if cookies:
            for k, v in cookies.iteritems():
                response.set_cookie(k, v)
        return response

    def render(self, template, qcontext=None, **kw):
        """ Lazy render of QWeb template.

        The actual rendering of the given template will occur at then end of
        the dispatching. Meanwhile, the template and/or qcontext can be
        altered or even replaced by a static response.

        :param basestring template: template to render
        :param dict qcontext: Rendering context to use
        """
        return Response(template=template, qcontext=qcontext, **kw)

    def not_found(self, description=None):
        """ Helper for 404 response, return its result from the method
        """
        return werkzeug.exceptions.NotFound(description)

def httprequest(f):
    """ 
        .. deprecated:: 8.0

        Use the ``route()`` decorator instead.
    """
    base = f.__name__.lstrip('/')
    if f.__name__ == "index":
        base = ""
    return route([base, base + "/<path:_ignored_path>"], type="http", auth="user", combine=True)(f)

#----------------------------------------------------------
# Controller and route registration
#----------------------------------------------------------
addons_module = {}
addons_manifest = {}
controllers_per_module = collections.defaultdict(list)

class ControllerType(type):
    def __init__(cls, name, bases, attrs):
        super(ControllerType, cls).__init__(name, bases, attrs)

        # flag old-style methods with req as first argument
        for k, v in attrs.items():
            if inspect.isfunction(v):
                spec = inspect.getargspec(v)
                first_arg = spec.args[1] if len(spec.args) >= 2 else None
                if first_arg in ["req", "request"]:
                    v._first_arg_is_req = True

        # store the controller in the controllers list
        name_class = ("%s.%s" % (cls.__module__, cls.__name__), cls)
        class_path = name_class[0].split(".")
        if not class_path[:2] == ["openerp", "addons"]:
            module = ""
        else:
            # we want to know all modules that have controllers
            module = class_path[2]
        # but we only store controllers directly inheriting from Controller
        if not "Controller" in globals() or not Controller in bases:
            return
        controllers_per_module[module].append(name_class)

class Controller(object):
    __metaclass__ = ControllerType

class EndPoint(object):
    def __init__(self, method, routing):
        self.method = method
        self.original = getattr(method, 'original_func', method)
        self.routing = routing
        self.arguments = {}

    @property
    def first_arg_is_req(self):
        # Backward for 7.0
        return getattr(self.method, '_first_arg_is_req', False)

    def __call__(self, *args, **kw):
        return self.method(*args, **kw)

def routing_map(modules, nodb_only, converters=None):
    routing_map = werkzeug.routing.Map(strict_slashes=False, converters=converters)
    for module in modules:
        if module not in controllers_per_module:
            continue

        for _, cls in controllers_per_module[module]:
            subclasses = cls.__subclasses__()
            subclasses = [c for c in subclasses if c.__module__.startswith('openerp.addons.') and c.__module__.split(".")[2] in modules]
            if subclasses:
                name = "%s (extended by %s)" % (cls.__name__, ', '.join(sub.__name__ for sub in subclasses))
                cls = type(name, tuple(reversed(subclasses)), {})

            o = cls()
            members = inspect.getmembers(o)
            for mk, mv in members:
                if inspect.ismethod(mv) and hasattr(mv, 'routing'):
                    routing = dict(type='http', auth='user', methods=None, routes=None)
                    methods_done = list()
                    routing_type = None
                    for claz in reversed(mv.im_class.mro()):
                        fn = getattr(claz, mv.func_name, None)
                        if fn and hasattr(fn, 'routing') and fn not in methods_done:
                            fn_type = fn.routing.get('type')
                            if not routing_type:
                                routing_type = fn_type
                            else:
                                if fn_type and routing_type != fn_type:
                                    _logger.warn("Subclass re-defines <function %s.%s> with different type than original."
                                                    " Will use original type: %r", fn.__module__, fn.__name__, routing_type)
                                fn.routing['type'] = routing_type
                            fn.original_func.routing_type = routing_type
                            methods_done.append(fn)
                            routing.update(fn.routing)
                    if not nodb_only or nodb_only == (routing['auth'] == "none"):
                        assert routing['routes'], "Method %r has not route defined" % mv
                        endpoint = EndPoint(mv, routing)
                        for url in routing['routes']:
                            if routing.get("combine", False):
                                # deprecated
                                url = o._cp_path.rstrip('/') + '/' + url.lstrip('/')
                                if url.endswith("/") and len(url) > 1:
                                    url = url[: -1]

                            routing_map.add(werkzeug.routing.Rule(url, endpoint=endpoint, methods=routing['methods']))
    return routing_map

#----------------------------------------------------------
# HTTP Sessions
#----------------------------------------------------------
class AuthenticationError(Exception):
    pass

class SessionExpiredException(Exception):
    pass

class Service(object):
    """
        .. deprecated:: 8.0
        Use ``dispatch_rpc()`` instead.
    """
    def __init__(self, session, service_name):
        self.session = session
        self.service_name = service_name

    def __getattr__(self, method):
        def proxy_method(*args):
            result = dispatch_rpc(self.service_name, method, args)
            return result
        return proxy_method

class Model(object):
    """
        .. deprecated:: 8.0
        Use the resistry and cursor in ``openerp.http.request`` instead.
    """
    def __init__(self, session, model):
        self.session = session
        self.model = model
        self.proxy = self.session.proxy('object')

    def __getattr__(self, method):
        self.session.assert_valid()
        def proxy(*args, **kw):
            # Can't provide any retro-compatibility for this case, so we check it and raise an Exception
            # to tell the programmer to adapt his code
            if not request.db or not request.uid or self.session.db != request.db \
                or self.session.uid != request.uid:
                raise Exception("Trying to use Model with badly configured database or user.")
                
            mod = request.registry.get(self.model)
            if method.startswith('_'):
                raise Exception("Access denied")
            meth = getattr(mod, method)
            cr = request.cr
            result = meth(cr, request.uid, *args, **kw)
            # reorder read
            if method == "read":
                if isinstance(result, list) and len(result) > 0 and "id" in result[0]:
                    index = {}
                    for r in result:
                        index[r['id']] = r
                    result = [index[x] for x in args[0] if x in index]
            return result
        return proxy

class OpenERPSession(werkzeug.contrib.sessions.Session):
    def __init__(self, *args, **kwargs):
        self.inited = False
        self.modified = False
        super(OpenERPSession, self).__init__(*args, **kwargs)
        self.inited = True
        self._default_values()
        self.modified = False

    def __getattr__(self, attr):
        return self.get(attr, None)
    def __setattr__(self, k, v):
        if getattr(self, "inited", False):
            try:
                object.__getattribute__(self, k)
            except:
                return self.__setitem__(k, v)
        object.__setattr__(self, k, v)

    def authenticate(self, db, login=None, password=None, uid=None):
        """
        Authenticate the current user with the given db, login and password. If successful, store
        the authentication parameters in the current session and request.

        :param uid: If not None, that user id will be used instead the login to authenticate the user.
        """

        if uid is None:
            wsgienv = request.httprequest.environ
            env = dict(
                base_location=request.httprequest.url_root.rstrip('/'),
                HTTP_HOST=wsgienv['HTTP_HOST'],
                REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
            )
            uid = dispatch_rpc('common', 'authenticate', [db, login, password, env])
        else:
            security.check(db, uid, password)
        self.db = db
        self.uid = uid
        self.login = login
        self.password = password
        request.uid = uid
        request.disable_db = False

        if uid: self.get_context()
        return uid

    def check_security(self):
        """
        Chech the current authentication parameters to know if those are still valid. This method
        should be called at each request. If the authentication fails, a ``SessionExpiredException``
        is raised.
        """
        if not self.db or not self.uid:
            raise SessionExpiredException("Session expired")
        security.check(self.db, self.uid, self.password)

    def logout(self, keep_db=False):
        for k in self.keys():
            if not (keep_db and k == 'db'):
                del self[k]
        self._default_values()

    def _default_values(self):
        self.setdefault("db", None)
        self.setdefault("uid", None)
        self.setdefault("login", None)
        self.setdefault("password", None)
        self.setdefault("context", {})

    def get_context(self):
        """
        Re-initializes the current user's session context (based on
        his preferences) by calling res.users.get_context() with the old
        context.

        :returns: the new context
        """
        assert self.uid, "The user needs to be logged-in to initialize his context"
        self.context = request.registry.get('res.users').context_get(request.cr, request.uid) or {}
        self.context['uid'] = self.uid
        self._fix_lang(self.context)
        return self.context

    def _fix_lang(self, context):
        """ OpenERP provides languages which may not make sense and/or may not
        be understood by the web client's libraries.

        Fix those here.

        :param dict context: context to fix
        """
        lang = context['lang']

        # inane OpenERP locale
        if lang == 'ar_AR':
            lang = 'ar'

        # lang to lang_REGION (datejs only handles lang_REGION, no bare langs)
        if lang in babel.core.LOCALE_ALIASES:
            lang = babel.core.LOCALE_ALIASES[lang]

        context['lang'] = lang or 'en_US'

    # Deprecated to be removed in 9

    """
        Damn properties for retro-compatibility. All of that is deprecated, all
        of that.
    """
    @property
    def _db(self):
        return self.db
    @_db.setter
    def _db(self, value):
        self.db = value
    @property
    def _uid(self):
        return self.uid
    @_uid.setter
    def _uid(self, value):
        self.uid = value
    @property
    def _login(self):
        return self.login
    @_login.setter
    def _login(self, value):
        self.login = value
    @property
    def _password(self):
        return self.password
    @_password.setter
    def _password(self, value):
        self.password = value

    def send(self, service_name, method, *args):
        """
        .. deprecated:: 8.0
        Use ``dispatch_rpc()`` instead.
        """
        return dispatch_rpc(service_name, method, args)

    def proxy(self, service):
        """
        .. deprecated:: 8.0
        Use ``dispatch_rpc()`` instead.
        """
        return Service(self, service)

    def assert_valid(self, force=False):
        """
        .. deprecated:: 8.0
        Use ``check_security()`` instead.

        Ensures this session is valid (logged into the openerp server)
        """
        if self.uid and not force:
            return
        # TODO use authenticate instead of login
        self.uid = self.proxy("common").login(self.db, self.login, self.password)
        if not self.uid:
            raise AuthenticationError("Authentication failure")

    def ensure_valid(self):
        """
        .. deprecated:: 8.0
        Use ``check_security()`` instead.
        """
        if self.uid:
            try:
                self.assert_valid(True)
            except Exception:
                self.uid = None

    def execute(self, model, func, *l, **d):
        """
        .. deprecated:: 8.0
        Use the resistry and cursor in ``openerp.addons.web.http.request`` instead.
        """
        model = self.model(model)
        r = getattr(model, func)(*l, **d)
        return r

    def exec_workflow(self, model, id, signal):
        """
        .. deprecated:: 8.0
        Use the resistry and cursor in ``openerp.addons.web.http.request`` instead.
        """
        self.assert_valid()
        r = self.proxy('object').exec_workflow(self.db, self.uid, self.password, model, signal, id)
        return r

    def model(self, model):
        """
        .. deprecated:: 8.0
        Use the resistry and cursor in ``openerp.addons.web.http.request`` instead.

        Get an RPC proxy for the object ``model``, bound to this session.

        :param model: an OpenERP model name
        :type model: str
        :rtype: a model object
        """
        if not self.db:
            raise SessionExpiredException("Session expired")

        return Model(self, model)

    def save_action(self, action):
        """
        This method store an action object in the session and returns an integer
        identifying that action. The method get_action() can be used to get
        back the action.

        :param the_action: The action to save in the session.
        :type the_action: anything
        :return: A key identifying the saved action.
        :rtype: integer
        """
        saved_actions = self.setdefault('saved_actions', {"next": 1, "actions": {}})
        # we don't allow more than 10 stored actions
        if len(saved_actions["actions"]) >= 10:
            del saved_actions["actions"][min(saved_actions["actions"])]
        key = saved_actions["next"]
        saved_actions["actions"][key] = action
        saved_actions["next"] = key + 1
        self.modified = True
        return key

    def get_action(self, key):
        """
        Gets back a previously saved action. This method can return None if the action
        was saved since too much time (this case should be handled in a smart way).

        :param key: The key given by save_action()
        :type key: integer
        :return: The saved action or None.
        :rtype: anything
        """
        saved_actions = self.get('saved_actions', {})
        return saved_actions.get("actions", {}).get(key)

def session_gc(session_store):
    if random.random() < 0.001:
        # we keep session one week
        last_week = time.time() - 60*60*24*7
        for fname in os.listdir(session_store.path):
            path = os.path.join(session_store.path, fname)
            try:
                if os.path.getmtime(path) < last_week:
                    os.unlink(path)
            except OSError:
                pass

#----------------------------------------------------------
# WSGI Layer
#----------------------------------------------------------
# Add potentially missing (older ubuntu) font mime types
mimetypes.add_type('application/font-woff', '.woff')
mimetypes.add_type('application/vnd.ms-fontobject', '.eot')
mimetypes.add_type('application/x-font-ttf', '.ttf')

class Response(werkzeug.wrappers.Response):
    """ Response object passed through controller route chain.

    In addition to the werkzeug.wrappers.Response parameters, this
    classe's constructor can take the following additional parameters
    for QWeb Lazy Rendering.

    :param basestring template: template to render
    :param dict qcontext: Rendering context to use
    :param int uid: User id to use for the ir.ui.view render call
    """
    default_mimetype = 'text/html'
    def __init__(self, *args, **kw):
        template = kw.pop('template', None)
        qcontext = kw.pop('qcontext', None)
        uid = kw.pop('uid', None)
        super(Response, self).__init__(*args, **kw)
        self.set_default(template, qcontext, uid)

    def set_default(self, template=None, qcontext=None, uid=None):
        self.template = template
        self.qcontext = qcontext or dict()
        self.uid = uid
        # Support for Cross-Origin Resource Sharing
        if request.endpoint and 'cors' in request.endpoint.routing:
            self.headers.set('Access-Control-Allow-Origin', request.endpoint.routing['cors'])
            methods = 'GET, POST'
            if request.endpoint.routing['type'] == 'json':
                methods = 'POST'
            elif request.endpoint.routing.get('methods'):
                methods = ', '.join(request.endpoint.routing['methods'])
            self.headers.set('Access-Control-Allow-Methods', methods)

    @property
    def is_qweb(self):
        return self.template is not None

    def render(self):
        view_obj = request.registry["ir.ui.view"]
        uid = self.uid or request.uid or openerp.SUPERUSER_ID
        return view_obj.render(request.cr, uid, self.template, self.qcontext, context=request.context)

    def flatten(self):
        self.response.append(self.render())
        self.template = None

class DisableCacheMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        def start_wrapped(status, headers):
            referer = environ.get('HTTP_REFERER', '')
            parsed = urlparse.urlparse(referer)
            debug = parsed.query.count('debug') >= 1

            new_headers = []
            unwanted_keys = ['Last-Modified']
            if debug:
                new_headers = [('Cache-Control', 'no-cache')]
                unwanted_keys += ['Expires', 'Etag', 'Cache-Control']

            for k, v in headers:
                if k not in unwanted_keys:
                    new_headers.append((k, v))

            start_response(status, new_headers)
        return self.app(environ, start_wrapped)

class Root(object):
    """Root WSGI application for the OpenERP Web Client.
    """
    def __init__(self):
        # Setup http sessions
        path = openerp.tools.config.session_dir
        _logger.debug('HTTP sessions stored in: %s', path)
        self.session_store = werkzeug.contrib.sessions.FilesystemSessionStore(path, session_class=OpenERPSession)
        self._loaded = False

    @lazy_property
    def nodb_routing_map(self):
        _logger.info("Generating nondb routing")
        return routing_map([''] + openerp.conf.server_wide_modules, True)

    def __call__(self, environ, start_response):
        """ Handle a WSGI request
        """
        if not self._loaded:
            self._loaded = True
            self.load_addons()
        return self.dispatch(environ, start_response)

    def load_addons(self):
        """ Load all addons from addons path containing static files and
        controllers and configure them.  """
        # TODO should we move this to ir.http so that only configured modules are served ?
        statics = {}

        for addons_path in openerp.modules.module.ad_paths:
            for module in sorted(os.listdir(str(addons_path))):
                if module not in addons_module:
                    manifest_path = os.path.join(addons_path, module, '__openerp__.py')
                    path_static = os.path.join(addons_path, module, 'static')
                    if os.path.isfile(manifest_path) and os.path.isdir(path_static):
                        manifest = ast.literal_eval(open(manifest_path).read())
                        manifest['addons_path'] = addons_path
                        _logger.debug("Loading %s", module)
                        if 'openerp.addons' in sys.modules:
                            m = __import__('openerp.addons.' + module)
                        else:
                            m = None
                        addons_module[module] = m
                        addons_manifest[module] = manifest
                        statics['/%s/static' % module] = path_static

        if statics:
            _logger.info("HTTP Configuring static files")
            app = werkzeug.wsgi.SharedDataMiddleware(self.dispatch, statics)
            self.dispatch = DisableCacheMiddleware(app)

    def setup_session(self, httprequest):
        # recover or create session
        session_gc(self.session_store)

        sid = httprequest.args.get('session_id')
        explicit_session = True
        if not sid:
            sid =  httprequest.headers.get("X-Openerp-Session-Id")
        if not sid:
            sid = httprequest.cookies.get('session_id')
            explicit_session = False
        if sid is None:
            httprequest.session = self.session_store.new()
        else:
            httprequest.session = self.session_store.get(sid)
        return explicit_session

    def setup_db(self, httprequest):
        db = httprequest.session.db
        # Check if session.db is legit
        if db:
            if db not in db_filter([db], httprequest=httprequest):
                _logger.warn("Logged into database '%s', but dbfilter "
                             "rejects it; logging session out.", db)
                httprequest.session.logout()
                db = None

        if not db:
            httprequest.session.db = db_monodb(httprequest)

    def setup_lang(self, httprequest):
        if not "lang" in httprequest.session.context:
            lang = httprequest.accept_languages.best or "en_US"
            lang = babel.core.LOCALE_ALIASES.get(lang, lang).replace('-', '_')
            httprequest.session.context["lang"] = lang

    def get_request(self, httprequest):
        # deduce type of request
        if httprequest.args.get('jsonp'):
            return JsonRequest(httprequest)
        if httprequest.mimetype == "application/json":
            return JsonRequest(httprequest)
        else:
            return HttpRequest(httprequest)

    def get_response(self, httprequest, result, explicit_session):
        if isinstance(result, Response) and result.is_qweb:
            try:
                result.flatten()
            except(Exception), e:
                if request.db:
                    result = request.registry['ir.http']._handle_exception(e)
                else:
                    raise

        if isinstance(result, basestring):
            response = Response(result, mimetype='text/html')
        else:
            response = result

        if httprequest.session.should_save:
            self.session_store.save(httprequest.session)
        # We must not set the cookie if the session id was specified using a http header or a GET parameter.
        # There are two reasons to this:
        # - When using one of those two means we consider that we are overriding the cookie, which means creating a new
        #   session on top of an already existing session and we don't want to create a mess with the 'normal' session
        #   (the one using the cookie). That is a special feature of the Session Javascript class.
        # - It could allow session fixation attacks.
        if not explicit_session and hasattr(response, 'set_cookie'):
            response.set_cookie('session_id', httprequest.session.sid, max_age=90 * 24 * 60 * 60)

        return response

    def dispatch(self, environ, start_response):
        """
        Performs the actual WSGI dispatching for the application.
        """
        try:
            httprequest = werkzeug.wrappers.Request(environ)
            httprequest.app = self

            explicit_session = self.setup_session(httprequest)
            self.setup_db(httprequest)
            self.setup_lang(httprequest)

            request = self.get_request(httprequest)

            def _dispatch_nodb():
                func, arguments = self.nodb_routing_map.bind_to_environ(request.httprequest.environ).match()
                request.set_handler(func, arguments, "none")
                result = request.dispatch()
                return result

            with request:
                db = request.session.db
                if db:
                    openerp.modules.registry.RegistryManager.check_registry_signaling(db)
                    try:
                        with openerp.tools.mute_logger('openerp.sql_db'):
                            ir_http = request.registry['ir.http']
                    except psycopg2.OperationalError:
                        # psycopg2 error. At this point, that means the
                        # database probably does not exists anymore. Log the
                        # user out and fall back to nodb
                        request.session.logout()
                        result = _dispatch_nodb()
                    else:
                        result = ir_http._dispatch()
                        openerp.modules.registry.RegistryManager.signal_caches_change(db)
                else:
                    result = _dispatch_nodb()

                response = self.get_response(httprequest, result, explicit_session)
            return response(environ, start_response)

        except werkzeug.exceptions.HTTPException, e:
            return e(environ, start_response)

    def get_db_router(self, db):
        if not db:
            return self.nodb_routing_map
        return request.registry['ir.http'].routing_map()

def db_list(force=False, httprequest=None):
    dbs = dispatch_rpc("db", "list", [force])
    return db_filter(dbs, httprequest=httprequest)

def db_filter(dbs, httprequest=None):
    httprequest = httprequest or request.httprequest
    h = httprequest.environ.get('HTTP_HOST', '').split(':')[0]
    d = h.split('.')[0]
    r = openerp.tools.config['dbfilter'].replace('%h', h).replace('%d', d)
    dbs = [i for i in dbs if re.match(r, i)]
    return dbs

def db_monodb(httprequest=None):
    """
        Magic function to find the current database.

        Implementation details:

        * Magic
        * More magic

        Returns ``None`` if the magic is not magic enough.
    """
    httprequest = httprequest or request.httprequest

    dbs = db_list(True, httprequest)

    # try the db already in the session
    db_session = httprequest.session.db
    if db_session in dbs:
        return db_session

    # if dbfilters was specified when launching the server and there is
    # only one possible db, we take that one
    if openerp.tools.config['dbfilter'] != ".*" and len(dbs) == 1:
        return dbs[0]
    return None

#----------------------------------------------------------
# RPC controller
#----------------------------------------------------------
class CommonController(Controller):

    @route('/jsonrpc', type='json', auth="none")
    def jsonrpc(self, service, method, args):
        """ Method used by client APIs to contact OpenERP. """
        return dispatch_rpc(service, method, args)

# register main wsgi handler
root = Root()
openerp.service.wsgi_server.register_wsgi_handler(root)

# vim:et:ts=4:sw=4:
