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

import re
import time
import datetime as DT

import turbogears as tg

from openerp import rpc

DT_SERVER_FORMATS = {
  'datetime' : '%Y-%m-%d %H:%M:%S',
  'date' : '%Y-%m-%d',
  'time' : '%H:%M:%S'
}

def get_datetime_format(kind="datetime"):
    """Get local datetime format.
    
    @param kind: type (date, time or datetime)
    @return: string
    
    @todo: cache formats to improve performance.
    @todo: extend user preferences to allow customisable date format (tiny server).
    """

    fmt = "%H:%M:%S"
    
    if kind != "time":
        fmt = tg.i18n.format.get_date_format("short", rpc.session.locale).replace("%y", "%Y")
    
    if kind == "datetime":
        fmt += " %H:%M:%S"
    
    return fmt

def format_datetime(value, kind="datetime", as_timetuple=False):
    """Convert date value to the local datetime considering timezone info.

    @param value: the date value
    @param kind: type of the date value (date, time or datetime)
    @param as_timetuple: return timetuple
    
    @type value: basestring or time.time_tuple)
    
    @return: string or timetuple
    """

    server_format = DT_SERVER_FORMATS[kind]
    local_format = get_datetime_format(kind)
    
    if not value:
        return ''
    
    if isinstance(value, (time.struct_time, tuple)):
        value = time.strftime(server_format, value)

    value = value.strip()

    # remove trailing miliseconds
    value = re.sub("(.*?)(\s+\d{2}:\d{2}:\d{2})(\.\d+)?$", "\g<1>\g<2>", value)

    # add time part in value if missing
    if kind == 'datetime' and not re.search('\s+\d{2}:\d{2}:\d{2}?$', value):
        value += ' 00:00:00'

    # remove time part from value
    elif kind == 'date':
        value = re.sub('\s+\d{2}:\d{2}:\d{2}(\.\d+)?$', '', value)

    value = time.strptime(value, server_format)

    if kind == "datetime" and 'tz' in rpc.session.context:
        try:
            import pytz
            lzone = pytz.timezone(str(rpc.session.context['tz']))
            szone = pytz.timezone(str(rpc.session.timezone))
            dt = DT.datetime(value[0], value[1], value[2], value[3], value[4], value[5], value[6])
            sdt = szone.localize(dt, is_dst=True)
            ldt = sdt.astimezone(lzone)
            value = ldt.timetuple()
        except:
            pass

    if as_timetuple:
        return value
    
    return time.strftime(local_format, value)

def parse_datetime(value, kind="datetime", as_timetuple=False):
    """Convert date value to the server datetime considering timezone info.

    @param value: the date value
    @param kind: type of the date value (date, time or datetime)
    @param as_timetuple: return timetuple
    
    @type value: basestring or time.time_tuple)
    
    @return: string or timetuple
    """
    
    server_format = DT_SERVER_FORMATS[kind]
    local_format = get_datetime_format(kind)

    if not value:
        return False

    if isinstance(value, (time.struct_time, tuple)):
        value = time.strftime(local_format, value)

    try:
        value = time.strptime(value, local_format)
    except:
        try:
            dt = list(time.localtime())
            dt[2] = int(value)
            value = tuple(dt)
        except:
            return False

    if kind == "datetime" and 'tz' in rpc.session.context:
        try:
            import pytz
            lzone = pytz.timezone(rpc.session.context['tz'])
            szone = pytz.timezone(rpc.session.timezone)
            dt = DT.datetime(value[0], value[1], value[2], value[3], value[4], value[5], value[6])
            ldt = lzone.localize(dt, is_dst=True)
            sdt = ldt.astimezone(szone)
            value = sdt.timetuple()
        except:
            pass

    if as_timetuple:
        return value
    
    return time.strftime(server_format, value)

def format_decimal(value, digits=2):
    return tg.i18n.format_decimal(value or 0.0, digits)

def parse_decimal(value):
    
    if isinstance(value, basestring):
        
        value = ustr(value)
        
        #deal with ' ' instead of u'\xa0' (SP instead of NBSP as grouping char)
        value = value.replace(' ', '')
        try:
            value = tg.i18n.format.parse_decimal(value)
        except ValueError, e:
            pass

    if not isinstance(value, float):
        return float(value)
    
    return value

# vim: ts=4 sts=4 sw=4 si et

