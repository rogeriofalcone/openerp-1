###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt. Ltd. (http://tinyerp.com) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
# Boston, MA  02111-1307, USA.
#
###############################################################################

import time
import datetime as DT

import turbogears as tg

from tinyerp import rpc

_DT_SERVER_FORMATS = {
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

    server_format = _DT_SERVER_FORMATS[kind]
    local_format = get_datetime_format(kind)
    
    if not value:
        return ''
    
    if isinstance(value, time.struct_time):
        value = time.strftime(server_format, value)
        
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
    
    server_format = _DT_SERVER_FORMATS[kind]
    local_format = get_local_datetime_format(kind)

    if not value:
        return False

    if isinstance(value, time.struct_time):
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
        #deal with ' ' instead of u'\xa0' (SP instead of NBSP as grouping char)
        value = value.replace(' ', '')
        try:
            value = tg.i18n.format.parse_decimal(value)
        except ValueError, e:
            pass

    if not isinstance(value, float):
        return float(value)
    
    return value
