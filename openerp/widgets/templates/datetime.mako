% if editable:
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td>
                <input type="text" id="${name}" name="${name}" 
                class="${css_class}" ${py.attrs(attrs, kind=kind, value=value)}/>
                % if error:
                <span class="fielderror">${error}</span>
                % endif
            </td>
            % if not attrs.get('disabled'):
            <td width="16" style="padding-left: 2px">
                <img id="${name}_trigger" width="16" height="16" alt="${_('Select')}" 
                src="/static/images/stock/stock_calendar.png" style="cursor: pointer;"/>
            </td>
            % endif
            % if not attrs.get('disabled'):
            <script type="text/javascript">
                Calendar.setup(
                {
                    inputField : "${name}",
                    ifFormat : "${format}",
                    button : "${name}_trigger",
                    showsTime: ${str(picker_shows_time).lower()}
                });
            </script>
            % endif
        </tr>
    </table>
% else:
    <span kind="${kind}" id="${name}" value="${value}">${value}</span>
% endif

