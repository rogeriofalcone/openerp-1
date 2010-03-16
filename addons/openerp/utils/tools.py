###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# The OpenERP web client is distributed under the "OpenERP Public License".
# It's based on Mozilla Public License Version (MPL) 1.1 with following
# restrictions:
#
# -   All names, links and logos of Tiny, Open ERP and Axelor must be
#     kept as in original distribution without any changes in all software
#     screens, especially in start-up page and the software header, even if
#     the application source code has been changed or updated or code has been
#     added.
#
# -   All distributions of the software must keep source code with OEPL.
#
# -   All integrations to any other software must keep source code with OEPL.
#
# If you need commercial licence to remove this kind of restriction please
# contact us.
#
# You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
#
###############################################################################

import os
import time
import tempfile
import datetime as DT

import rpc


def expr_eval(string, context={}):
    context.update(uid=rpc.session.uid,
                   current_date=time.strftime('%Y-%m-%d'),
                   time=time,
                   datetime=DT)
    if isinstance(string, basestring):
        return eval(string.replace("'active_id'", "active_id"),
                    context)
    else:
        return string

def node_attributes(node):
    if not node.hasAttributes(): return {}
    attrs = node.attributes
    # localName can be a unicode string, we're using attribute names as
    # **kwargs keys and python-level kwargs don't take unicode keys kindly
    # (they blow up) so we need to ensure all keys are ``str``
    return dict([(str(attrs.item(i).localName), attrs.item(i).nodeValue)
                 for i in range(attrs.length)])

def xml_locate(expr, ref):
    """Simple xpath locator.

    >>> xml_locate("/form[1]/field[2]", doc)
    >>> xml_locate("/form[1]", doc)

    @param expr: simple xpath with tag name and index
    @param ref: reference node

    @return: list of nodes
    """

    if '/' not in expr:
        name, index = expr.split('[')
        index = int(index.replace(']', ''))

        nodes = [n for n in ref.childNodes if n.localName == name]
        try:
            return nodes[index-1]
        except Exception, e:
            return []

    parts = expr.split('/')
    for part in parts:
        if part in ('', '.'):
#            for node in ref.childNodes:
#               if node.nodeType == node.ELEMENT_NODE:
#                   ref = node
            continue
        ref = xml_locate(part, ref)

    return [ref]

def get_node_xpath(node):

    pn = node.parentNode
    xp = '/' + node.localName
    root = xp + '[1]'

    if pn and pn.localName and pn.localName != 'view':
        xp = get_node_xpath(pn) + xp

    nodes = xml_locate(root, node.parentNode)
    xp += '[%s]' % (nodes.index(node) + 1)

    return xp

def get_size(sz):
    """
    Return the size in a human readable format
    """
    if not sz:
        return False

    units = ('bytes', 'Kb', 'Mb', 'Gb')
    if isinstance(sz,basestring):
        sz=len(sz)
    s, i = float(sz), 0
    while s >= 1024 and i < len(units)-1:
        s = s / 1024
        i = i + 1
    return "%0.2f %s" % (s, units[i])

def context_with_concurrency_info(context, concurrency_info):
    ctx = (context or {}).copy()
    if not concurrency_info:
        return ctx
    if isinstance(concurrency_info, tuple):
        concurrency_info = [concurrency_info]
    ctx['__last_update'] = dict(concurrency_info)
    return ctx


class TempFileName(str):
    '''A string representing a temporary file name that will be deleted when object is deleted'''
    def __new__(cls, suffix="", prefix=tempfile.template, dir=None, text=False):
        fd, fn = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
        os.close(fd)
        return str.__new__(cls, fn)

    def __del__(self):
        import os   # ensure os module exists
        if os.path.exists(str(self)):
            os.unlink(str(self))

    def __copy__(self):
        return self

    def __deepcopy__(self, visit):
        return self


# vim: ts=4 sts=4 sw=4 si et
