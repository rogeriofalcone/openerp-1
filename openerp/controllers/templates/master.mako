<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<%! show_header_footer=True %>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    
% for css in widget_css:
    ${css.display()}
% endfor

    <script type="text/javascript">
        window.SCRIPT_PATH = "${cp.request.app.script_name}";
    </script>

    <script type="text/javascript" src="${py.url('/static/javascript/MochiKit/MochiKit.js')}"></script>
    <script type="text/javascript" src="${py.url('/static/javascript/MochiKit/DragAndDrop.js')}"></script>
    <script type="text/javascript" src="${py.url('/static/javascript/MochiKit/Resizable.js')}"></script>
    <script type="text/javascript" src="${py.url('/static/javascript/MochiKit/Sortable.js')}"></script>
    
% for js in widget_javascript.get('head', []):
    ${js.display()}
% endfor

    <link href="${py.url('/static/css/style.css')}" rel="stylesheet" type="text/css"/>
    <link href="${py.url('/static/css/menu.css')}" rel="stylesheet" type="text/css"/>
    <link href="${py.url('/static/css/tips.css')}" rel="stylesheet" type="text/css"/>

    <!--[if IE]>
    <link href="${py.url('/static/css/style-ie.css')}" rel="stylesheet" type="text/css"/>
    <![endif]-->
        
    <script type="text/javascript" src="${py.url('/static/javascript/master.js')}"></script>
    <script type="text/javascript" src="${py.url('/static/javascript/menu.js')}"></script>
    <script type="text/javascript" src="${py.url('/static/javascript/ajax.js')}"></script>
    <script type="text/javascript" src="${py.url('/static/javascript/tips.js')}"></script>
    
    ${self.header()}

</head>

<body>

<%
# put in try block to prevent improper redirection on connection refuse error
try:
    shortcuts = cp.root.shortcuts.my()
    requests, requests_message = cp.root.requests.my()
except:
    shortcuts = []
    requests = []
    requests_message = None
%>

% for js in widget_javascript.get('bodytop', []):
    ${js.display()}
% endfor

<table id="container" border="0" cellpadding="0" cellspacing="0">
    % if context.get('show_header_footer', self.attr.show_header_footer):
    <tr>
           <td>
            <table id="header" class="header" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td rowspan="2">
                        ${cp.root.get_logo()|n}
                    </td>
                    <td align="right" valign="top" nowrap="nowrap" height="24">
                        <table class="menu_connection" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td>
                                    <a href="http://openerp.com" target="_blank" title="OpenERP - Open Source Management Solution" style="padding: 0px;">
                                        <img src="${py.url('/static/images/openerp_small.png')}" border="0" width="86" height="24"/></a>
                                </td>
                                <td width="26" class="menu_connection_right" nowrap="nowrap">
                                    <div style="width: 26px;"/>
                                </td>
                                <td class="menu_connection_welcome" nowrap="norwap">
                                    ${_("Welcome %(user)s", user=rpc.session.user_name or 'guest')}
                                </td>
                                <td class="menu_connection_links" nowrap="norwap">
                                    <a href="${py.url('/')}">${_("Home")}</a>
                                    <a href="${py.url('/pref/create')}">${_("Preferences")}</a>
                                    <a href="${py.url('/about')}">${_("About")}</a>
                                    <a href="${py.url('/logout')}">${_("Logout")}</a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    % if rpc.session.is_logged():
                    <td align="right" valign="middle" style="padding-right: 4px;">
                        ${_("Requests:")} <a href="${py.url('/requests')}">${requests_message}</a>
                    </td>
                    % endif
                </tr>
                <tr>
                    <td colspan="2" nowrap="nowrap">

                        <table width="100%" cellspacing="0" cellpadding="0" id="menu_header">
                            <tr>
                                <td width="5%" id="menu_header_menu" nowrap="nowrap">
                                    <a href="${py.url('/menu')}">${_("MAIN MENU")}</a>
                                </td>
                                <td width="5%" id="menu_header_shortcuts" nowrap="nowrap">
                                    <a href="${py.url('/shortcuts')}">${_("SHORTCUTS")}</a>
                                </td>
                                <td width="26" class="menu_header_shortcuts_left" nowrap="nowrap"/>
                                % if rpc.session.is_logged():
                                <td nowrap="nowrap">
                                    <table id="shortcuts" class="menubar" border="0" cellpadding="0" cellspacing="0">
                                        <tr>
                                            % for i, sc in enumerate(shortcuts):
                                                % if i<6:
                                            <td nowrap="nowrap">
                                                <a href="${py.url('/tree/open', id=sc['res_id'], model='ir.ui.menu')}">${sc['name']}</a>
                                            </td>
                                                % endif
                                            % endfor
                                            % if len(shortcuts)>6:
                                            <td id="shortcuts_menu" nowrap="nowrap">
                                                <a href="javascript: void(0)">>></a>
                                                <div class="submenu" id="shortcuts_submenu">
                                                    % for sc in shortcuts[6:]:
                                                    <a href="${py.url('/tree/open', id=sc['res_id'], model='ir.ui.menu')}">${sc['name']}</a>
                                                    % endfor
                                                </div>
                                            </td>
                                            % endif
                                        </tr>
                                    </table>
                                    % if len(shortcuts)>6:
                                    <script type="text/javascript">
                                        new Menu('shortcuts_menu', 'shortcuts_submenu');
                                    </script>
                                    % endif
                                </td>
                                % endif
                                <td>
                                    &nbsp;
                                </td>
                                <td align="right">
                                    % if cp.root.shortcuts.can_create():
                                    <a href="${py.url('/shortcuts/add', id=rpc.session.active_id)}" id="menu_header">${_("[ADD]")}</a>
                                    % endif
                                </td>
                            </tr>
                        </table>

                    </td>
                </tr>
            </table>
        </td>
    </tr>
    % endif
    <tr>
        <td>
            ${self.content()}
        </td>
    </tr>
    % if context.get('show_header_footer', self.attr.show_header_footer):
    <tr>
        <td>
            <div id="footer">
${_("Copyright &copy; 2007-TODAY Tiny ERP Pvt. Ltd. All Rights Reserved.")|n}
${_("More Information on %s") % ("""<a href="http://openerp.com">http://openerp.com</a>.""")|n}
<br/>
${_("The web client is developed by %(axelor)s and %(tiny)s.", 
    tiny="""Tiny (<a href="http://tiny.be">http://tiny.be</a>)""",
    axelor="""Axelor (<a href="http://axelor.com">http://axelor.com</a>)""")|n}
<br/>
${_("Running Server:")} <span>${rpc.session.protocol}://${rpc.session.host}:${rpc.session.port} - database: ${rpc.session.db or 'N/A'}</span><br/>
            </div>
        </td>
    </tr>
    % endif
</table>

% for js in widget_javascript.get('bodybottom', []):
    ${js.display()}
% endfor

</body>
</html>
