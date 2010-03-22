<table id="${name}" class="gridview" width="100%" cellspacing="0" cellpadding="0">
    % if pageable:
    <tr class="pagerbar">
        <td colspan="2" class="pagerbar-cell" align="right">${pager.display()}</td>
    </tr>
    % endif

    <tr>
        <td colspan="2">
            <table id="${name}_grid" class="grid" width="100%" cellspacing="0" cellpadding="0">

                <thead>
                    <tr class="grid-header">
                        % if selector:
                        <th width="1" class="grid-cell selector">
                            % if selector=='checkbox':
                            <input type="checkbox" class="checkbox grid-record-selector" onclick="new ListView('${name}').checkAll(!this.checked)"/>
                            % endif
                            % if selector!='checkbox':
                            <span>&nbsp;</span>
                            % endif
                        </th>
                        % endif
                        % if editable:
                        <th class="grid-cell selector"><div style="width: 0px;"></div></th>
                        % endif
                        % for (field, field_attrs) in headers:
                        % if field == 'button':
                        	<th class="grid-cell"></th>
                        %else: 
                        	<th id="grid-data-column/${(name != '_terp_list' or None) and (name + '/')}${field}" class="grid-cell ${field_attrs.get('type', 'char')}" kind="${field_attrs.get('type', 'char')}" style="cursor: pointer;" onclick="new ListView('${name}').sort_by_order('${field}')">${field_attrs['string']}</th>
                    	% endif
                        % endfor
                        % if buttons:
                        <th class="grid-cell button"><div style="width: 0px;"></div></th>
                        % endif
                        % if editable:
                        <th class="grid-cell selector"><div style="width: 0px;"></div></th>
                        % endif
                    </tr>
                </thead>

                <tbody>
                    <%def name="make_editors(data=None)">
                    % if editable and editors:
                    <tr class="grid-row editors">
                        % if selector:
                        <td class="grid-cell selector">&nbsp;</td>
                        % endif
                        <td class="grid-cell selector" style="text-align: center; padding: 0px;">
                            <!-- begin hidden fields -->
                            % for field, field_attrs in hiddens:
                            ${editors[field].display()}
                            % endfor
                            <!-- end of hidden fields -->
                            <img src="/openerp/static/images/listgrid/save_inline.gif" class="listImage editors" border="0" title="${_('Update')}" onclick="new ListView('${name}').save(${(data and data['id']) or 'null'})"/>
                        </td>
                        % for i, (field, field_attrs) in enumerate(headers):
                        	% if field=='button':
	                        	<td class="grid-cell">
	                        	</td>
	                        % else:
	                        	<td class="grid-cell ${field_attrs.get('type', 'char')}">
	                            	${editors[field].display()}
	                        	</td>
                        	% endif
                        % endfor
                        <td class="grid-cell selector" style="text-align: center; padding: 0px;">
                            <img src="/openerp/static/images/listgrid/delete_inline.gif" class="listImage editors" border="0" title="${_('Cancel')}" onclick="new ListView('${name}').reload()"/>
                        </td>
                    </tr>
                    % endif
                    </%def>

                    <%def name="make_row(data)">
                    <tr class="grid-row" record="${data['id']}" style="cursor: pointer;">
                        % if selector:
                        <td class="grid-cell selector">
                            <input type="${selector}" class="${selector} grid-record-selector" id="${name}/${data['id']}" name="${(checkbox_name or None) and name}" value="${data['id']}"/>
                        </td>
                        % endif
                        % if editable:
                        <td class="grid-cell selector">
                            % if not editors:
                            <img src="/openerp/static/images/listgrid/edit_inline.gif" class="listImage" border="0" title="${_('Edit')}" onclick="editRecord(${data['id']}, '${source}')"/>
                            % elif not editors:
                            <img src="/openerp/static/images/listgrid/edit_inline.gif" border="0" title="${_('Edit')}"/>
                            % endif                            
                            % if editors:
                            <img src="/openerp/static/images/listgrid/edit_inline.gif" class="listImage" border="0" title="${_('Edit')}" onclick="new ListView('${name}').edit(${data['id']})"/>
                            % endif
                        </td>
                        % endif
                        % for i, (field, field_attrs) in enumerate(headers):
                        %if field=='button':
                        	<td class="grid-cell"><span>${buttons[field_attrs-1].display(parent_grid=name, **buttons[field_attrs-1].params_from(data))}</span></td>
                        %else:
	                        <td class="grid-cell ${field_attrs.get('type', 'char')}" style="${(data[field].color or None) and 'color: ' + data[field].color};" sortable_value="${data[field].get_sortable_text()}">
								<span>${data[field].display()}</span>
	                        </td>
                        % endif
                        % endfor
                        
                        % if editable:
                        <td class="grid-cell selector">
                            <img src="/openerp/static/images/listgrid/delete_inline.gif" class="listImage" border="0" title="${_('Delete')}" onclick="new ListView('${name}').remove(${data['id']})"/>
                        </td>
                        % endif
                    </tr>
                    </%def>

                    % if edit_inline == -1:
                    ${make_editors()}
                    % endif

                    % for i, d in enumerate(data):
                        % if d['id'] == edit_inline:
                        ${make_editors(d)}
                        % endif
                        % if d['id'] != edit_inline:
                        ${make_row(d)}
                        % endif
                    % endfor

                    % if concurrency_info:
                    <tr style="display: none">
                        <td>${concurrency_info.display()}</td>
                    </tr>
                    % endif

                    % for i in range(0, min_rows - len(data)):
                    <tr class="grid-row">
                        % if selector:
                        <td width="1%" class="grid-cell selector">&nbsp;</td>
                        % endif
                        % if editable:
                        <td style="text-align: center" class="grid-cell selector">&nbsp;</td>
                        % endif
                        % for i, (field, field_attrs) in enumerate(headers):
                        % if field == 'button':
                        	<td class="grid-cell button">&nbsp;</td>
                    	% else:
                        	<td class="grid-cell">&nbsp;</td>
                    	% endif
                        % endfor
                        % if editable:
                        <td style="text-align: center" class="grid-cell selector">&nbsp;</td>
                        % endif
                    </tr>
                    % endfor

                </tbody>

                % if field_total:
                <tfoot>
                    <tr class="field_sum">
                        % if selector:
                        <td width="1%" class="grid-cell">&nbsp;</td>
                        % endif
                        % if editable:
                        <td width="1%" class="grid-cell">&nbsp;</td>
                        % endif
                        % for i, (field, field_attrs) in enumerate(headers):
                        % if field == 'button':
                        	<td class="grid-cell button"><div style="width: 0px;"></div></td>
                        % else:
                        <td class="grid-cell" style="text-align: right; padding: 2px;" nowrap="nowrap">
                             % if 'sum' in field_attrs:
                                 % for key, val in field_total.items():
                                     % if field == key:
                                     <span style="border-top: 1px inset ; display: block; padding: 0px 1px;">${val[1]}</span>
                                     % endif
                                 % endfor
                             % endif
                             % if 'sum' not in field_attrs:
                             &nbsp;
                             % endif
                        </td>
                        % endif
                        % endfor
                        % if editable:
                        <td width="1%" class="grid-cell">&nbsp;</td>
                        % endif
                    </tr>
                </tfoot>
                % endif

            </table>

            <script type="text/javascript">
                	<% 
                		import itertools 
                	   	from itertools import chain	
                	%>
                	
                	% if data and 'sequence' in map(lambda x: x[0], chain(headers,hiddens)):
                 		var drag = getElementsByTagAndClassName('tr','grid-row');
                		for(var grid=0; grid < drag.length; grid++) 
                		{
						    new Draggable(drag[grid], {revert:true, ghosting:true});
							new Droppable(drag[grid], {accept: [drag[grid].className], ondrop: new ListView('${name}').dragRow, hoverclass: 'grid-rowdrop'});
 						}
                	% endif
            </script>
        </td>
    </tr>

    % if pageable:
    <tr class="pagerbar">
        <td class="pagerbar-cell pagerbar-links" align="left">
            <a href="javascript: void(0)" onclick="new ListView('${name}').importData()">${_("Import")}</a> | <a href="javascript: void(0)" onclick="new ListView('${name}').exportData()">${_("Export")}</a>
        </td>
        <td class="pagerbar-cell" align="right">${pager.display(pager_id=2)}</td>
    </tr>
    % endif
</table>

