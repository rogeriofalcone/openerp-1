# -*- coding: utf-8 -*-
"""
Collection of configuration-related helpers for the OpenERP Web Client
"""
import os
import os.path
import platform
import sys

import babel.localedata

import openobject.paths

__all__ = ['configure_babel', 'find_file', 'ConfigurationError']

class ConfigurationError(Exception):
    pass

def configure_babel():
    """ If we are in a py2exe bundle, rather than babel being installed in
    a site-packages directory in an unzipped form with all its meta- and
    package- data it is split between the code files within py2exe's archive
    file and the metadata being stored at the toplevel of the py2exe
    distribution.
    """
    if not hasattr(sys, 'frozen'): return

    # the locale-specific data files are in babel/localedata/*.dat, babel
    # finds these data files via the babel.localedata._dirname filesystem
    # path.
    babel.localedata._dirname = openobject.paths.root('babel', 'localedata')

def expand(filepath):
    return os.path.expanduser(
        os.path.expandvars(
            filepath))

SETTINGS_ENVIRON_KEY = 'OPENERP_WEB_SETTINGS'
def find_file():
    """ Attempts to find and return the path to an OpenERP Web Client
    configuration file, according to the discovery process described below.

    If it can not find any configuration file, or a step of the configuration
    discovery process fails, raises ``ConfigurationError``.

    Configuration File Discovery Process for the OpenERP Web Client (steps
    tried in order, the function returns as soon as a step yields a result):

    #. If the environment variable ``OPENERP_WEB_SETTINGS`` is set, checks
       that it is a valid file path and returns it. If
       ``OPENERP_WEB_SETTINGS`` is not a valid file path, raises an error.
    #. On unices (Linux, Mac OS X, BSDs), looks for the file
       ``~/.openerp-web``
    #. On Windows, looks for the file ``%APPDATA%\openerp-web\config.ini``
    #. On unices, looks for the file ``/etc/openerp-web.cfg``
    #. Looks for the file ``openerp-web.cfg`` in the client's own directory

    :return: configuration file path
    :rtype: str
    """
    # environ
    if SETTINGS_ENVIRON_KEY in os.environ:
        config_path = os.environ[SETTINGS_ENVIRON_KEY]
        expanded_path = expand(config_path)
        if not os.path.isfile(expanded_path):
            raise ConfigurationError(
                "Path '%s' found in environment key '%s' does not seem to be "
                "a valid configuration file" % (
                    config_path, SETTINGS_ENVIRON_KEY))
        return expanded_path

    # per-user config
    if platform.system() == 'Windows':
        config_path = os.path.join(
            expand('%APPDATA%'), 'openerp-web', 'config.ini')
        if os.path.isfile(config_path):
            return config_path
    else:
        config_path = expand('~/.openerp-web')
        if os.path.isfile(config_path):
            return config_path

    # system
    if platform.system() != 'Windows':
        config_path = '/etc/openerp-web.cfg'
        if os.path.isfile(config_path):
            return config_path

    # local fallback
    config_path = openobject.paths.root('openerp-web.cfg')
    if os.path.isfile(config_path):
        return config_path

    raise ConfigurationError("Failed to find a configuration file for "
                             "the OpenERP Web Client")
