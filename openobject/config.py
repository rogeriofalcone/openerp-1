# -*- coding: utf-8 -*-
"""
Collection of configuration-related helpers for the OpenERP Web Client
"""
import sys

import babel.localedata

import openobject.paths

__all__ = ['configure_babel']

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
