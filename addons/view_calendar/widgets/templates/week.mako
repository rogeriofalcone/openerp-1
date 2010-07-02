<table border="0" style="border: none;" id="Calendar">
    <tr>
        <td width="100%" style="width: 100%; padding: 0;">
            <div class="box-a calendar-a">
            <p class="side">
                <a class="button-b" href="javascript:void(0)" title="${_('Today...')}" onclick="getCalendar('${selected_day.today().isoformat()}', 'day')">${_("Today")}</a>
            </p>
            <ul class="head">
                <li>
                    <a href="javascript: void(0)" title="${_('Month Calendar...')}" onclick="getCalendar(null, 'month')">${_("Month")}</a>
                </li>
                <li>
                    <a class="active" href="javascript: void(0)" title="${_('Week Calendar...')}">${_("Week")}</a>
                </li>
                <li>
                    <a href="javascript: void(0)" title="${_('Day Calendar...')}" onclick="getCalendar(null, 'day')">${_("Day")}</a>
                </li>
            </ul>
            <div class="inner">
                <p class="paging-a">
                    <span class="one">
                        <a class="first" href="javascript: void(0)"></a>
                        <small>|</small>
                        <a class="prev" href="javascript: void(0)" onclick="getCalendar('${week.prev()[0].isoformat()}')"></a>
                    </span>
                    <small>|</small>
                    <span class="two">
                        <a class="next" href="javascript: void(0)" onclick="getCalendar('${week.next()[0].isoformat()}')"></a>
                        <small>|</small>
                        <a class="last" href="javascript: void(0)"></a>
                    </span>
                </p>
                <h4>
                    <span>
                        <small>${week}</small>
                    </span>
                </h4>
            </div>
            <table border="0" id="calContainer" width="100%">
                <tr>
                    <td id="calMainArea" valign="top">
                        <input type="hidden" id="_terp_selected_day" name="_terp_selected_day" value="${selected_day.isoformat()}"/>
                        <input type="hidden" id="_terp_selected_mode" name="_terp_selected_mode" value="week"/>
                        <input type="hidden" id="_terp_calendar_fields" name="_terp_calendar_fields" value="${calendar_fields}"/>
                        % if concurrency_info:
                            ${concurrency_info.display()}
                        % endif
                        <div id="calWeek" class="calWeek" dtFormat="${date_format}"><span></span>
                            <div id="calHeaderSect">
                                % for day in week:
                                <div dtDay="${day.isoformat()}">${day.name} ${day.day}</div>
                                % endfor
                            </div>
                            <div id="calAllDaySect">
                                % for evt in events:
                                    % if evt.dayspan > 0:
                                        <div nRecordID="${evt.record_id}" 
                                            nDaySpan="${evt.dayspan}" 
                                            dtStart="${str(evt.starts)}" 
                                            dtEnd="${str(evt.ends)}" 
                                            title="${evt.description}"
                                            nCreationDate="${evt.create_date}"
                                            nCreationId="${evt.create_uid}"
                                            nWriteDate="${evt.write_date}"
                                            nWriteId="${evt.write_uid}" 
                                            style="background-color: ${evt.color}; -moz-border-radius: 5px;" 
                                            class="calEvent allDay">${evt.title}</div>
                                    % endif
                                % endfor
                            </div>
                            <div id="calBodySect">
                                % for evt in events:
                                    % if evt.dayspan == 0:
                                <div nRecordID="${evt.record_id}" 
                                    dtStart="${str(evt.starts)}" 
                                    dtEnd="${str(evt.ends)}"
                                    nCreationDate="${evt.create_date}"
                                    nCreationId="${evt.create_uid}"
                                    nWriteDate="${evt.write_date}"
                                    nWriteId="${evt.write_uid}"
                                    style="background-color: ${evt.color}; -moz-border-radius: 5px;" 
                                    class="calEvent noAllDay">
                                   <div style="height: 10px;" class="calEventTitle">${evt.starts.strftime('%I:%M %P')} - ${evt.title}</div>
                                   <div class="calEventDesc">${evt.description}</div>
                                   <div class="calEventGrip"></div>
                                </div>
                                    % endif
                                % endfor
                            </div>
                        </div>
                        <script type="text/javascript">
                            CAL_INSTANCE = new WeekCalendar();
                        </script>
                    </td>
                </tr>
            </table>
        </div>
        </td>
        <td id="calSidebar"valign="top">
            <%include file="sidebar.mako" />
        </td>
    </tr>
</table>
