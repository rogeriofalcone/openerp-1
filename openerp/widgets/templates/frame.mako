% for w in hiddens:
<div style="display: none;">${display_child(w)}</div>
% endfor
<table width="100%" border="0" class='fields'>
    % for row in table:
    <tr>
        % for attrs, widget  in row:
        <td ${py.attrs(attrs)}>
            % if isinstance(widget, basestring):
                % if attrs.get('title'):
                <sup style="color: darkgreen;">?</sup>
                % endif
                ${(widget or '') and widget + ':'}
            % endif
            % if not isinstance(widget, basestring) and widget.visible:
            ${display_child(widget)}
            % endif
        </td>
        % endfor
    </tr>
    % endfor
</table>

