# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
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
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website as controllers
import datetime
import dateutil.parser as dparser
from collections import OrderedDict
import re
import werkzeug.utils

controllers = controllers()

class website_event(http.Controller):
    @http.route(['/event/<model("event.event"):event>/track/<model("event.track"):track>'], type='http', auth="public", website=True, multilang=True)
    def event_track_view(self, event, track, **post):
        track_obj = request.registry.get('event.track')
        track = track_obj.browse(request.cr, openerp.SUPERUSER_ID, track.id, context=request.context)
        values = { 'track': track, 'event': track.event_id, 'main_object': track }
        return request.website.render("website_event_track.track_view", values)

    # TODO: not implemented
    @http.route(['/event/<model("event.event"):event>/agenda/'], type='http', auth="public", website=True, multilang=True)
    def event_agenda(self, event, tag=None, **post):
        #To make timeslot according to given track time
        def algo_for_timetable(new_start_date, new_end_date, new_schedule):
            #If new time in range of start and end time, it make two slot
            #and remove old element.
            def insert_time(time, new_schedule):
                for index,ct in enumerate(time):
                    for index2,dt in enumerate(new_schedule):
                        st = dt[0]
                        et = dt[1]
                        if st == ct or et == ct:break
                        if st < ct and et > ct:
                            new_schedule.pop(index2)
                            new_schedule.insert(index2, [ct, et])
                            new_schedule.insert(index2, [st, ct])
                            break
                return new_schedule
            if not new_schedule:
                new_schedule.append([new_start_date, new_end_date])
                return new_schedule
            first_start_date = new_schedule[0][0]
            last_end_date = new_schedule[-1][1]

            #totally outter
            if first_start_date >= new_start_date and new_end_date >= last_end_date:
                if not new_start_date == first_start_date:
                    new_schedule.insert(0, [new_start_date, first_start_date])
                if not last_end_date ==  new_end_date:
                    new_schedule.append([last_end_date, new_end_date])
                return new_schedule
            
            #lower outer
            if first_start_date >= new_end_date:
                new_schedule.insert(0, [new_start_date, new_end_date])
                if not new_end_date == first_start_date:
                    new_schedule.insert(1, [new_end_date, first_start_date])
                return new_schedule
            
            # upper outer
            if new_start_date >= last_end_date:
                if not last_end_date == new_start_date:
                    new_schedule.append([last_end_date, new_start_date])
                new_schedule.append([new_start_date, new_end_date])
                return new_schedule
            
            #When inner time
            if first_start_date <= new_start_date and last_end_date >= new_end_date:
                new_schedule = insert_time([new_start_date, new_end_date], new_schedule)
                return new_schedule
            
            #when start date is more and end date in range
            if first_start_date > new_start_date and last_end_date >= new_end_date:
                new_schedule.insert(0, [new_start_date, first_start_date])
                new_schedule = insert_time([new_end_date], new_schedule)
                return new_schedule
            
            #when end date is more and start date in range
            if new_end_date > last_end_date and new_start_date >= first_start_date:
                 new_schedule = insert_time([new_start_date], new_schedule)
                 new_schedule.append([last_end_date, new_end_date])
                 return new_schedule

        request.cr.execute('''
            Select id, location_id, groupby_datetime, duration, name, date from (
                Select id, location_id, to_char(date_trunc('hour',date),'mm-dd-yy hh AM') as
                groupby_datetime, duration, name, event_id, date, count(*) as tot from event_track
                group by event_id, duration, id, location_id, date, date_trunc('hour',date)
                order by date, date_trunc('hour',date)
            ) 
            event_query where event_query.event_id = %s 
                group by  event_query.location_id, event_query.id, 
                  event_query.groupby_datetime, event_query.duration,event_query.name, event_query.date;
            ''',(event.id,))
        
        fetch_tracks = request.cr.fetchall()
        
        request.cr.execute('''
        select count(*), date_trunc('day',date) from event_track where event_id = %s group by date_trunc('day',date) order by  date_trunc('day',date)
        ''',(event.id,))
        talks = request.cr.fetchall()
        
        unsort_tracks = {}
        room_list = []
        new_schedule = {}
        location_object = request.registry.get('event.track.location')
        event_track_obj = request.registry.get('event.track')
        
        #Make all possible timeslot for each day.
        for track in fetch_tracks:
            room_list.append(track[1])
            if not new_schedule.has_key(track[2][:8]):
                new_schedule[track[2][:8]] = []
            start_time = datetime.datetime.strptime(track[5], '%Y-%m-%d %H:%M:%S')
            end_time = start_time + datetime.timedelta(minutes = int(track[3]))
            new_schedule[track[2][:8]] = algo_for_timetable(start_time, end_time, new_schedule[track[2][:8]])

        #Add timeslot as key to track
        for key in new_schedule.keys():
            unsort_tracks[key] = OrderedDict()
            for value in new_schedule[key]:
                unsort_tracks[key][value[0].strftime('%H:%M')+" - "+value[1].strftime('%H:%M')] = []
        
        #Add track to its related time slot and day.
        for track in fetch_tracks:
            start_time = datetime.datetime.strptime(track[5], '%Y-%m-%d %H:%M:%S')
            end_time = start_time + datetime.timedelta(minutes = int(track[3]))
            secret_key = None
            row_span = 0
            for index, value in enumerate(new_schedule[track[2][:8]]):
                if value[0] <= start_time and value[1] > start_time:
                    keys = unsort_tracks[track[2][:8]].keys()
                    secret_key = keys[index]
                    row_span = index
                if value[1] == end_time and secret_key:
                    if not index == row_span:
                        index = index + 1  
                    event_tracks = event_track_obj.browse(request.cr, openerp.SUPERUSER_ID, track[0], context=request.context)
                    color =  0 if event_tracks.color > 9 else event_tracks.color
                    unsort_tracks[track[2][:8]][secret_key].append({
                             'id': track[0],
                             'title': track[4],
                             'time': track[5],
                             'location_id': track[1],
                             'duration':track[3],
                             'location_id': track[1],
                             'end_time': end_time,
                             'speaker_ids': [s.name for s in event_tracks.speaker_ids],
                             'row_span': index - row_span,
                             'color': color,
                             'publish': not event_tracks.website_published
                       })
                
        #Get All Locations and make room_list contain unique value.
        room_list = list(set(room_list))
        room_list.sort()
        rooms = []
        for room in room_list:
            if room:rooms.append([room, location_object.browse(request.cr, openerp.SUPERUSER_ID, room).name])
        
        #For rowspan calculate all td which will not display in future.
        #Sort track according to location(to display under related location). 
        skip_td = {}
        for track in unsort_tracks.keys():
            skip_td[track] = {}
            key1 = unsort_tracks[track].keys()
            for tra in unsort_tracks[track].keys():
                list1 = unsort_tracks[track][tra]
                unsort_tracks[track][tra] = sorted(list1, key=lambda x: x['location_id'])
                for i in unsort_tracks[track][tra]:
                    if i['row_span']:
                        skip_time = key1[key1.index(tra)+1: key1.index(tra)+i['row_span']]
                        if not skip_td[track].has_key(i['location_id']):
                            skip_td[track] [i['location_id']] = []
                        skip_td[track] [i['location_id']] = skip_td[track] [i['location_id']] + skip_time

        #Remove repeated element in list if any.
        format_date = []
        for skip in skip_td.keys():
            format_date.append((datetime.datetime.strptime(skip, '%m-%d-%y')).strftime("%d %B, %Y"))
            for loc in skip_td[skip].keys():
                skip_td[skip][loc] = list(set(skip_td[skip][loc]))
        values = {
            'event': event,
            'main_object': event,
            'room_list': rooms,
            'days': unsort_tracks,
            'skip_td': skip_td,
            'talks':talks,
            'format_date':format_date
        }
        return request.website.render("website_event_track.agenda", values)

    @http.route([
        '/event/<model("event.event"):event>/track/',
        '/event/<model("event.event"):event>/track/tag/<model("event.track.tag"):tag>'
        ], type='http', auth="public", website=True, multilang=True)
    def event_tracks(self, event, tag=None, **post):
        searches = {}
        if tag:
            searches.update(tag=tag.id)
            track_obj = request.registry.get('event.track')
            track_ids = track_obj.search(request.cr, request.uid,
                [("id", "in", [track.id for track in event.track_ids]), ("tag_ids", "=", tag.id)], context=request.context)
            tracks = track_obj.browse(request.cr, request.uid, track_ids, context=request.context)
        else:
            tracks = event.track_ids

        def html2text(html):
            return re.sub(r'<[^>]+>', "", html)
        values = {
            'event': event,
            'main_object': event,
            'tracks': tracks,
            'tags': event.tracks_tag_ids,
            'searches': searches,
            'html2text': html2text
        }
        return request.website.render("website_event_track.tracks", values)

    @http.route(['/event/<model("event.event"):event>/track_proposal/'], type='http', auth="public", website=True, multilang=True)
    def event_track_proposal(self, event, **post):
        values = { 'event': event }
        return request.website.render("website_event_track.event_track_proposal", values)

    @http.route(['/event/<model("event.event"):event>/track_proposal/post'], type='http', auth="public", methods=['POST'], website=True, multilang=True)
    def event_track_proposal_post(self, event, **post):
        cr, uid, context = request.cr, request.uid, request.context

        tobj = request.registry['event.track']

        tags = []
        for tag in event.allowed_track_tag_ids:
            if post.get('tag_'+str(tag.id)):
                tags.append(tag.id)

        e = werkzeug.utils.escape
        track_description = '''<section data-snippet-id="text-block">
    <div class="container">
        <div class="row">
            <div class="col-md-12 text-center">
                <h2>%s</h2>
            </div>
            <div class="col-md-12">
                <p>%s</p>
            </div>
            <div class="col-md-12">
                <h3>About The Author</h3>
                <p>%s</p>
            </div>
        </div>
    </div>
</section>''' % (e(post['track_name']), 
            e(post['description']), e(post['biography']))

        track_id = tobj.create(cr, openerp.SUPERUSER_ID, {
            'name': post['track_name'],
            'event_id': event.id,
            'tag_ids': [(6, 0, tags)],
            'user_id': False,
            'description': track_description
        }, context=context)

        tobj.message_post(cr, openerp.SUPERUSER_ID, [track_id], body="""Proposed By: %s<br/>
          Mail: <a href="mailto:%s">%s</a><br/>
          Phone: %s""" % (e(post['partner_name']), e(post['email_from']), 
            e(post['email_from']), e(post['phone'])), context=context)

        track = tobj.browse(cr, uid, track_id, context=context)
        values = {'track': track, 'event':event}
        return request.website.render("website_event_track.event_track_proposal_success", values)
