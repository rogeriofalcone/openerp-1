<table border="0" id="calContainer" width="100%" xmlns:py="http://purl.org/kid/ns#">
<tr>
    <td width="100%" id="calNavigation">
        <table width="100%" class="toolbar">
            <tr>
                <td nowrap="nowrap">
                    <img height="16" width="16" class="button" src="/static/images/stock/gtk-go-back.png" 
                        onclick="getCalendar('${days[0].prev().isoformat()}', null)"/>
                </td>
                <td nowrap="nowrap">
                    <button type="button" title="${_('Today...')}" 
                        onclick="getCalendar('${days[0].today().isoformat()}', 'day')">Today</button>
                </td>
                <td nowrap="nowrap">
                    <img height="16" width="16" class="button" src="/static/images/stock/gtk-go-forward.png" 
                        onclick="getCalendar('${days[-1].next().isoformat()}', null)"/>
                </td>
                <td nowrap="nowrap" width="100%"><strong>${title}</strong></td>
                <td nowrap="nowrap">
                    <img title="${_('Zoom In')}" height="16" width="16" src="/static/images/stock-disabled/gtk-zoom-in.png" py:if="mode == 'day'"/>
                    <img title="${_('Zoom In')}" height="16" width="16" class="button" src="/static/images/stock/gtk-zoom-in.png"  py:if="mode != 'day'"
                        onclick="ganttZoomIn()"/>
                    
                    <img title="${_('Zoom Out')}" height="16" width="16" src="/static/images/stock-disabled/gtk-zoom-out.png" py:if="mode == '5years'"/>
                    <img title="${_('Zoom Out')}" height="16" width="16" class="button" src="/static/images/stock/gtk-zoom-out.png" py:if="mode != '5years'"
                        onclick="ganttZoomOut()"/>
                </td>
            </tr>
        </table>
        <input type="hidden" id="_terp_selected_day" name="_terp_selected_day" value="${selected_day.isoformat()}"/>
        <input type="hidden" id="_terp_selected_mode" name="_terp_selected_mode" value="${mode}"/>
        <input type="hidden" id="_terp_calendar_fields" name="_terp_calendar_fields" value="${ustr(calendar_fields)}"/>
        <input type="hidden" id="_terp_gantt_level" name="_terp_gantt_level" value="${ustr(level)}"/>
        <input type="hidden" py:if="concurrency_info" py:replace="concurrency_info.display()"/>
    </td>
</tr>
<tr>
    <td id="calMainArea" valign="top">

        <div id="calGantt" class="calGantt" dtFormat="${date_format}" dtStart="${days[0].isoformat()}" dtRange="${len(days)}"><span></span>

            <div id="calHeaderSect">
                <div class="calTitle" py:for="count, header in headers" nCount="${count}">${header}</div>
                <div class="calSubTitle" py:for="header in subheaders">${header}</div>
            </div>

            <div id="calBodySect">
                <div py:for="group in groups" class="calGroup"
                    nRecordID="${group['id']}"
                    items="${str(group['items'])}"
                    model="${group['model']}"
                    title="${group['title']}"/>
                <div py:for="evt in events" class="calEvent"
                    nRecordID="${evt.record_id}"
                    nDaySpan="${evt.dayspan}"
                    dtStart="${str(evt.starts)}"
                    dtEnd="${str(evt.ends)}"
                    title="${evt.title}"
                    style="background-color: ${evt.color}"/>
            </div>
        </div>

        <div py:replace="groupbox.display()"/>
            <div id="calSearchOptions">
                <table border="0">
                    <tr>
                        <td>
                            <input type="checkbox" class="checkbox" 
                                id="_terp_use_search" name="_terp_use_search" 
                                checked="${(use_search or None) and 'checked'}" 
                                onclick="getCalendar()"/>
                        </td>
                        <td>Apply search filter</td>
                    </tr>
                </table>
            </div>


        <script type="text/javascript">
            CAL_INSTANCE = new GanttCalendar();
        </script>

    </td>
</tr>
</table>
