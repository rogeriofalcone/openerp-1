<%inherit file="/openerp/controllers/templates/base_dispatch.mako"/>

<%def name="header()">
    <title>OpenERP</title>

    <script type="text/javascript" src="/openerp/static/javascript/accordion.js"></script>
    <script type="text/javascript" src="/openerp/static/javascript/treegrid.js"></script>
    <script type="text/javascript" src="/openerp/static/javascript/notebook/notebook.js"></script>
    
    <script type="text/javascript">
        var DOCUMENT_TO_LOAD = "${load_content}";
        var CAL_INSTANCE = null;

        jQuery(document).ready(function () {
            // Don't load doc if there is a hash-url, it takes precedence
            if(DOCUMENT_TO_LOAD && !hashUrl()) {
                openLink(DOCUMENT_TO_LOAD);
            }
        });
        
    </script>
</%def>

<%def name="content()">

    <div id="root">
        <table id="content" class="three-a open" width="100%" height="100%">
            <tr>
                <%include file="header.mako"/>
            </tr>
            <tr>
                <td id="main_nav" colspan="3">
                    <div id="applications_menu">
                        <ul>
                            %for parent in parents:
                                <li>
                                    <a href="${py.url('/openerp/menu', active=parent['id'])}"
                                       target="_top" class="${parent.get('active', '')}">
                                        <span>${parent['name']}</span>
                                    </a>
                                </li>
                            % endfor
                        </ul>
                    </div>
                </td>
            </tr>
            % if tools is not None:
                <tr>
                    <td id="secondary" class="sidenav-open">
                        <div class="wrap">
                            <ul id="sidenav-a" class="accordion">
                                % for tool in tools:
                                    % if tool.get('action'):
                                      <li class="accordion-title" id="${tool['id']}">
                                    % else:
                                      <li class="accordion-title">
                                    % endif
                                        <span>${tool['name']}</span>
                                    </li>
                                    <li class="accordion-content" id="content_${tool['id']}">
                                       ${tool['tree'].display()}
                                    </li>
                                % endfor
                            </ul>
                            <script type="text/javascript">
                                new Accordion("sidenav-a");
                            </script>
                        </div>
                    </td>
                    <td id="primary" width="100%" height="100%">
                        <div class="wrap">
                            <div id="appContent"></div>
                        </div>
                    </td>
                </tr>
            % else:
                <tr>
                    <td colspan="3" height="100%" valign="top">
                        <table width="100%">
                            <tr>
                                <td id="primary" width="70%">
                                    <div class="wrap" style="padding: 10px;">
                                        <ul class="sections-a">
                                            % for parent in parents:
                                                <li class="web_dashboard" id="${parent['id']}">
                                                    <span class="wrap">
                                                        <a href="${py.url('/openerp/menu', active=parent['id'])}" target="_top">
                                                            <table width="100%" height="100%" cellspacing="0" cellpadding="1">
                                                                <tr>
                                                                    <td align="center" style="height: 100px;">
                                                                        % if parent.get('web_icon_datas'):
                                                                            <img id="web_icon" src="data:image/png;base64,${parent['web_icon_datas']}"/>
                                                                        % endif
                                                                        %if parent.get('web_icon_hover_datas'):
                                                                            <img id="web_icon_hover" src="data:image/png;base64,${parent['web_icon_hover_datas']}"/>
                                                                        % endif
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td>
                                                                        <span>
                                                                            <strong>${parent['name']}</strong>
                                                                        </span>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </a>
                                                    </span>
                                                    % if parent.get('web_icon_hover_datas'):
                                                        <script type="text/javascript">
                                                            jQuery(document).ready(function(){
                                                                jQuery("li.web_dashboard#${parent['id']}").mouseover(function() {
                                                                    jQuery(this).find('#web_icon').hide();
                                                                    jQuery(this).find('#web_icon_hover').show();
                                                                });
                                                                jQuery("li.web_dashboard#${parent['id']}").mouseout(function(){
                                                                    jQuery(this).find('#web_icon').show();
                                                                    jQuery(this).find('#web_icon_hover').hide();
                                                                });
                                                            });
                                                        </script>
                                                    % endif
                                                </li>
                                            % endfor
                                        </ul>
                                    </div>
                                </td>
                                <td class="tertiary">
                                    <div class="wrap" style="padding: 10px;">
                                        <ul class="split-a">
                                            <li class="one">
                                                <a class="cta-a" href="http://www.openerp.com/services/subscribe-onsite" target="_blank">
                                                    <span>
                                                        <strong>${_('Use On-Site')}</strong>
                                                        ${_("Get the OpenERP Warranty")}
                                                    </span>
                                                </a>
                                            </li>
                                            <li class="two">
                                                <a class="cta-a" href="http://www.openerp.com/online" target="_blank">
                                                    <span>
                                                        <strong>${_('Use Online')}</strong>
                                                        ${_("Subscribe and start")}
                                                    </span>
                                                </a>
                                            </li>
                                        </ul>
                                    </div>
                                    <div class="box-a">
                                        <ul class="side">
                                        </ul>
                                        % for widget in widgets:
                                            <div class="sideheader-a" style="padding: 0">
                                                <h2>${widget['title']}</h2>
                                                ${widget['content']|n}
                                            </div>
                                        % endfor
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            % endif
            <tr>
                <td id="footer_section" colspan="3">
                    % if cp.config('server.environment') == 'development':
                        <div class="footer-a">
                            <p class="one">
                                <span>${rpc.session.protocol}://${_("%(user)s", user=rpc.session.loginname)}@${rpc.session.host}:${rpc.session.port}</span>
                            </p>
                            <p class="powered">${_("Powered by %(openerp)s ",
                                                openerp="""<a target="_blank" href="http://www.openerp.com/">openerp.com</a>""")|n}</p>
                        </div>
                    % else:
                        <div class="footer-b">
                            <p class="powered">${_("Powered by %(openerp)s ",
                                                openerp="""<a target="_blank" href="http://www.openerp.com/">openerp.com</a>""")|n}</p>
                        </div>
                    % endif
                </td>
            </tr>
        </table>
    </div>
</%def>

