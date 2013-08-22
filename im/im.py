# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
import openerp.tools.config
import openerp.modules.registry
import openerp.addons.web.http as http
from openerp.addons.web.http import request
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import datetime
from openerp.osv import osv, fields
import time
import logging
import json
import select

_logger = logging.getLogger(__name__)

def listen_channel(cr, channel_name, handle_message, check_stop=(lambda: False), check_stop_timer=60.):
    """
        Begin a loop, listening on a PostgreSQL channel. This method does never terminate by default, you need to provide a check_stop
        callback to do so. This method also assume that all notifications will include a message formated using JSON (see the
        corresponding notify_channel() method).

        :param db_name: database name
        :param channel_name: the name of the PostgreSQL channel to listen
        :param handle_message: function that will be called when a message is received. It takes one argument, the message
            attached to the notification.
        :type handle_message: function (one argument)
        :param check_stop: function that will be called periodically (see the check_stop_timer argument). If it returns True
            this function will stop to watch the channel.
        :type check_stop: function (no arguments)
        :param check_stop_timer: The maximum amount of time between calls to check_stop_timer (can be shorter if messages
            are received).
    """
    try:
        conn = cr._cnx
        cr.execute("listen " + channel_name + ";")
        cr.commit();
        stopping = False
        while not stopping:
            if check_stop():
                stopping = True
                break
            if select.select([conn], [], [], check_stop_timer) == ([],[],[]):
                pass
            else:
                conn.poll()
                while conn.notifies:
                    message = json.loads(conn.notifies.pop().payload)
                    handle_message(message)
    finally:
        try:
            cr.execute("unlisten " + channel_name + ";")
            cr.commit()
        except:
            pass # can't do anything if that fails

def notify_channel(cr, channel_name, message):
    """
        Send a message through a PostgreSQL channel. The message will be formatted using JSON. This method will
        commit the given transaction because the notify command in Postgresql seems to work correctly when executed in
        a separate transaction (despite what is written in the documentation).

        :param cr: The cursor.
        :param channel_name: The name of the PostgreSQL channel.
        :param message: The message, must be JSON-compatible data.
    """
    cr.commit()
    cr.execute("notify " + channel_name + ", %s", [json.dumps(message)])
    cr.commit()

POLL_TIMER = 30
DISCONNECTION_TIMER = POLL_TIMER + 5
WATCHER_ERROR_DELAY = 10

class LongPollingController(http.Controller):

    @http.route('/longpolling/im/poll', type="json", auth="none")
    def poll(self, last=None, users_watch=None, db=None, uid=None, password=None, uuid=None):
        assert_uuid(uuid)
        if not openerp.evented:
            raise Exception("Not usable in a server not running gevent")
        from openerp.addons.im.watcher import ImWatcher
        if db is not None:
            openerp.service.security.check(db, uid, password)
        else:
            uid = request.session.uid
            db = request.session.db

        registry = openerp.modules.registry.RegistryManager.get(db)
        with registry.cursor() as cr:
            registry.get('im.user').im_connect(cr, uid, uuid=uuid, context=request.context)
            my_id = registry.get('im.user').get_by_user_id(cr, uid, uuid or uid, request.context)["id"]
        num = 0
        while True:
            with registry.cursor() as cr:
                res = registry.get('im.message').get_messages(cr, uid, last, users_watch, uuid=uuid, context=request.context)
            if num >= 1 or len(res["res"]) > 0:
                return res
            last = res["last"]
            num += 1
            ImWatcher.get_watcher(res["dbname"]).stop(my_id, users_watch or [], POLL_TIMER)

    @http.route('/longpolling/im/activated', type="json", auth="none")
    def activated(self):
        return not not openerp.evented

    @http.route('/longpolling/im/gen_uuid', type="json", auth="none")
    def gen_uuid(self):
        import uuid
        return "%s" % uuid.uuid1()

def assert_uuid(uuid):
    if not isinstance(uuid, (str, unicode, type(None))) and uuid != False:
        raise Exception("%s is not a uuid" % uuid)


class im_message(osv.osv):
    _name = 'im.message'

    _order = "date desc"

    _columns = {
        'message': fields.char(string="Message", size=200, required=True),
        'from_id': fields.many2one("im.user", "From", required= True, ondelete='cascade'),
        'to_id': fields.many2one("im.user", "To", required=True, select=True, ondelete='cascade'),
        'date': fields.datetime("Date", required=True, select=True),
    }

    _defaults = {
        'date': lambda *args: datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    }
    
    def get_messages(self, cr, uid, last=None, users_watch=None, uuid=None, context=None):
        assert_uuid(uuid)
        users_watch = users_watch or []

        # complex stuff to determine the last message to show
        users = self.pool.get("im.user")
        my_id = users.get_by_user_id(cr, uid, uuid or uid, context=context)["id"]
        c_user = users.browse(cr, openerp.SUPERUSER_ID, my_id, context=context)
        if last:
            if c_user.im_last_received < last:
                users.write(cr, openerp.SUPERUSER_ID, my_id, {'im_last_received': last}, context=context)
        else:
            last = c_user.im_last_received or -1

        # how fun it is to always need to reorder results from read
        mess_ids = self.search(cr, openerp.SUPERUSER_ID, [['id', '>', last], ['to_id', '=', my_id]], order="id", context=context)
        mess = self.read(cr, openerp.SUPERUSER_ID, mess_ids, ["id", "message", "from_id", "date"], context=context)
        index = {}
        for i in xrange(len(mess)):
            index[mess[i]["id"]] = mess[i]
        mess = []
        for i in mess_ids:
            mess.append(index[i])

        if len(mess) > 0:
            last = mess[-1]["id"]
        users_status = users.read(cr, openerp.SUPERUSER_ID, users_watch, ["im_status"], context=context)
        return {"res": mess, "last": last, "dbname": cr.dbname, "users_status": users_status}

    def post(self, cr, uid, message, to_user_id, uuid=None, context=None):
        assert_uuid(uuid)
        my_id = self.pool.get('im.user').get_by_user_id(cr, uid, uuid or uid)["id"]
        self.create(cr, openerp.SUPERUSER_ID, {"message": message, 'from_id': my_id, 'to_id': to_user_id}, context=context)
        notify_channel(cr, "im_channel", {'type': 'message', 'receiver': to_user_id})
        return False

class im_user(osv.osv):
    _name = "im.user"

    def _im_status(self, cr, uid, ids, something, something_else, context=None):
        res = {}
        current = datetime.datetime.now()
        delta = datetime.timedelta(0, DISCONNECTION_TIMER)
        data = self.read(cr, openerp.SUPERUSER_ID, ids, ["im_last_status_update", "im_last_status"], context=context)
        for obj in data:
            last_update = datetime.datetime.strptime(obj["im_last_status_update"], DEFAULT_SERVER_DATETIME_FORMAT)
            res[obj["id"]] = obj["im_last_status"] and (last_update + delta) > current
        return res

    def search_users(self, cr, uid, domain, fields, limit, context=None):
        # do not user openerp.SUPERUSER_ID, reserved to normal users
        found = self.pool.get('res.users').search(cr, uid, domain, limit=limit, context=context)
        found = self.get_by_user_ids(cr, uid, found, context=context)
        return self.read(cr, uid, found, fields, context=context)

    def im_connect(self, cr, uid, uuid=None, context=None):
        assert_uuid(uuid)
        return self._im_change_status(cr, uid, True, uuid, context)

    def im_disconnect(self, cr, uid, uuid=None, context=None):
        assert_uuid(uuid)
        return self._im_change_status(cr, uid, False, uuid, context)

    def _im_change_status(self, cr, uid, new_one, uuid=None, context=None):
        assert_uuid(uuid)
        id = self.get_by_user_id(cr, uid, uuid or uid, context=context)["id"]
        current_status = self.read(cr, openerp.SUPERUSER_ID, id, ["im_status"], context=None)["im_status"]
        self.write(cr, openerp.SUPERUSER_ID, id, {"im_last_status": new_one, 
            "im_last_status_update": datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
        if current_status != new_one:
            notify_channel(cr, "im_channel", {'type': 'status', 'user': id})
        return True

    def get_by_user_id(self, cr, uid, id, context=None):
        ids = self.get_by_user_ids(cr, uid, [id], context=context)
        return ids[0]

    def get_by_user_ids(self, cr, uid, ids, context=None):
        user_ids = [x for x in ids if isinstance(x, int)]
        uuids = [x for x in ids if isinstance(x, (str, unicode))]
        users = self.search(cr, openerp.SUPERUSER_ID, ["|", ["user", "in", user_ids], ["uuid", "in", uuids]], context=None)
        records = self.read(cr, openerp.SUPERUSER_ID, users, ["user", "uuid"], context=None)
        inside = {}
        for i in records:
            if i["user"]:
                inside[i["user"][0]] = True
            elif ["uuid"]:
                inside[i["uuid"]] = True
        not_inside = {}
        for i in ids:
            if not (i in inside):
                not_inside[i] = True
        for to_create in not_inside.keys():
            if isinstance(to_create, int):
                created = self.create(cr, openerp.SUPERUSER_ID, {"user": to_create}, context=context)
                records.append({"id": created, "user": [to_create, ""]})
            else:
                created = self.create(cr, openerp.SUPERUSER_ID, {"uuid": to_create}, context=context)
                records.append({"id": created, "uuid": to_create})
        return records

    def assign_name(self, cr, uid, uuid, name, context=None):
        assert_uuid(uuid)
        id = self.get_by_user_id(cr, uid, uuid or uid, context=context)["id"]
        self.write(cr, openerp.SUPERUSER_ID, id, {"assigned_name": name}, context=context)
        return True

    def _get_name(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.assigned_name
            if record.user:
                res[record.id] = record.user.name
                continue
        return res

    _columns = {
        'name': fields.function(_get_name, type='char', size=200, string="Name", store=True, readonly=True),
        'assigned_name': fields.char(string="Assigned Name", size=200, required=False),
        'image': fields.related('user', 'image_small', type='binary', string="Image", readonly=True),
        'user': fields.many2one("res.users", string="User", select=True, ondelete='cascade'),
        'uuid': fields.char(string="UUID", size=50, select=True),
        'im_last_received': fields.integer(string="Instant Messaging Last Received Message"),
        'im_last_status': fields.boolean(strint="Instant Messaging Last Status"),
        'im_last_status_update': fields.datetime(string="Instant Messaging Last Status Update"),
        'im_status': fields.function(_im_status, string="Instant Messaging Status", type='boolean'),
    }

    _defaults = {
        'im_last_received': -1,
        'im_last_status': False,
        'im_last_status_update': lambda *args: datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    }
